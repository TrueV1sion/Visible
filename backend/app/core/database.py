from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import QueuePool
import structlog
from .config import settings

logger = structlog.get_logger("database")

# Create engine with connection pooling
engine = create_engine(
    settings.SQLALCHEMY_DATABASE_URI,
    poolclass=QueuePool,
    pool_size=20,
    max_overflow=0,
    pool_pre_ping=True,
    pool_recycle=300,
    echo=settings.ENVIRONMENT == "development"
)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@event.listens_for(engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    """Set database pragmas for SQLite (if used for testing)."""
    if "sqlite" in str(dbapi_connection):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()


@event.listens_for(engine, "before_cursor_execute")
def log_queries(conn, cursor, statement, parameters, context, executemany):
    """Log slow queries for performance monitoring."""
    context._query_start_time = time.time()


@event.listens_for(engine, "after_cursor_execute")
def log_slow_queries(conn, cursor, statement, parameters, context, executemany):
    """Log queries that take longer than threshold."""
    total_time = time.time() - context._query_start_time
    
    if total_time > 1.0:  # Log queries slower than 1 second
        logger.warning(
            "Slow database query",
            duration=total_time,
            statement=statement[:200]  # Truncate long statements
        )


def get_db() -> Session:
    """Dependency for getting database session."""
    db = SessionLocal()
    try:
        yield db
    except Exception as e:
        logger.error("Database session error", error=str(e))
        db.rollback()
        raise
    finally:
        db.close()


async def check_db_health() -> Dict[str, Any]:
    """Check database connectivity and performance."""
    try:
        db = SessionLocal()
        start_time = time.time()
        
        # Test basic connectivity
        db.execute("SELECT 1")
        
        # Test query performance
        db.execute("SELECT COUNT(*) FROM users")
        
        response_time = time.time() - start_time
        db.close()
        
        status = "healthy"
        if response_time > 1.0:
            status = "slow"
        if response_time > 5.0:
            status = "degraded"
        
        return {
            "status": status,
            "response_time": response_time,
            "connection_pool": {
                "size": engine.pool.size(),
                "checked_in": engine.pool.checkedin(),
                "checked_out": engine.pool.checkedout(),
                "overflow": engine.pool.overflow(),
                "invalid": engine.pool.invalid()
            }
        }
        
    except Exception as e:
        logger.error("Database health check failed", error=str(e))
        return {
            "status": "unhealthy",
            "error": str(e)
        }


def create_tables():
    """Create all database tables."""
    from ..models import Base
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables created")


def drop_tables():
    """Drop all database tables (use with caution)."""
    from ..models import Base
    Base.metadata.drop_all(bind=engine)
    logger.warning("Database tables dropped")