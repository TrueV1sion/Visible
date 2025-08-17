from sqlalchemy import create_engine, event, text
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import QueuePool
from sqlalchemy.exc import SQLAlchemyError
import structlog
import time
from typing import Dict, Any, Generator
from .config import settings
from .exceptions import DatabaseError

logger = structlog.get_logger("database")

# Create engine with optimized configuration
engine = create_engine(
    settings.SQLALCHEMY_DATABASE_URI,
    poolclass=QueuePool,
    pool_size=20,
    max_overflow=10,
    pool_pre_ping=True,
    pool_recycle=300,
    echo=settings.ENVIRONMENT == "development",
    connect_args={
        "connect_timeout": 10,
        "application_name": "battlecard_platform"
    }
)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@event.listens_for(engine, "connect")
def set_postgresql_pragma(dbapi_connection, connection_record):
    """Set PostgreSQL-specific connection settings."""
    with dbapi_connection.cursor() as cursor:
        # Set timezone
        cursor.execute("SET timezone TO 'UTC'")
        
        # Set reasonable timeouts
        cursor.execute("SET statement_timeout = '30s'")
        cursor.execute("SET lock_timeout = '10s'")
        
        # Enable query plan caching
        cursor.execute("SET plan_cache_mode = 'auto'")


@event.listens_for(engine, "before_cursor_execute")
def log_queries(conn, cursor, statement, parameters, context, executemany):
    """Log database queries for performance monitoring."""
    context._query_start_time = time.time()
    
    # Log slow queries immediately for debugging
    if settings.ENVIRONMENT == "development":
        logger.debug(
            "Executing query",
            statement=statement[:200]  # Truncate long statements
        )


@event.listens_for(engine, "after_cursor_execute")
def log_slow_queries(conn, cursor, statement, parameters, context, executemany):
    """Log queries that take longer than threshold."""
    total_time = time.time() - context._query_start_time
    
    if total_time > 1.0:  # Log queries slower than 1 second
        logger.warning(
            "Slow database query",
            duration=total_time,
            statement=statement[:200],
            parameters=str(parameters)[:100] if parameters else None
        )
    elif total_time > 0.5:  # Log moderately slow queries at debug level
        logger.debug(
            "Moderate database query",
            duration=total_time,
            statement=statement[:100]
        )


def get_db() -> Generator[Session, None, None]:
    """Dependency for getting database session with proper error handling."""
    db = SessionLocal()
    try:
        yield db
    except SQLAlchemyError as e:
        logger.error("Database session error", error=str(e))
        db.rollback()
        raise DatabaseError(
            message=f"Database operation failed: {str(e)}",
            operation="session_management"
        )
    except Exception as e:
        logger.error("Unexpected database error", error=str(e))
        db.rollback()
        raise DatabaseError(
            message="Unexpected database error occurred",
            operation="session_management"
        )
    finally:
        db.close()


async def check_db_health() -> Dict[str, Any]:
    """Check database connectivity and performance."""
    try:
        db = SessionLocal()
        start_time = time.time()
        
        # Test basic connectivity
        db.execute(text("SELECT 1"))
        
        # Test table access
        result = db.execute(text("SELECT COUNT(*) FROM users")).scalar()
        user_count = result or 0
        
        # Test query performance
        db.execute(text("SELECT pg_stat_database.datname, pg_stat_database.numbackends FROM pg_stat_database WHERE datname = current_database()"))
        
        response_time = time.time() - start_time
        db.close()
        
        # Determine health status
        status = "healthy"
        if response_time > 1.0:
            status = "slow"
        if response_time > 5.0:
            status = "degraded"
        
        return {
            "status": status,
            "response_time": round(response_time, 3),
            "user_count": user_count,
            "connection_pool": {
                "size": engine.pool.size(),
                "checked_in": engine.pool.checkedin(),
                "checked_out": engine.pool.checkedout(),
                "overflow": engine.pool.overflow(),
                "invalid": engine.pool.invalid()
            },
            "timestamp": time.time()
        }
        
    except SQLAlchemyError as e:
        logger.error("Database health check failed", error=str(e))
        return {
            "status": "unhealthy",
            "error": str(e),
            "error_type": "SQLAlchemyError",
            "timestamp": time.time()
        }
    except Exception as e:
        logger.error("Database health check failed with unexpected error", error=str(e))
        return {
            "status": "unhealthy",
            "error": str(e),
            "error_type": type(e).__name__,
            "timestamp": time.time()
        }


def create_tables():
    """Create all database tables."""
    try:
        from ..models import Base
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created successfully")
    except Exception as e:
        logger.error("Failed to create database tables", error=str(e))
        raise DatabaseError(
            message=f"Failed to create tables: {str(e)}",
            operation="table_creation"
        )


def drop_tables():
    """Drop all database tables (use with extreme caution)."""
    try:
        from ..models import Base
        Base.metadata.drop_all(bind=engine)
        logger.warning("Database tables dropped")
    except Exception as e:
        logger.error("Failed to drop database tables", error=str(e))
        raise DatabaseError(
            message=f"Failed to drop tables: {str(e)}",
            operation="table_deletion"
        )


async def init_database():
    """Initialize database with default data."""
    try:
        from ..models.user import User, UserRole
        from ..core.security import get_password_hash
        
        db = SessionLocal()
        
        # Check if admin user exists
        admin = db.query(User).filter(User.role == UserRole.ADMIN).first()
        
        if not admin:
            # Create default admin user
            admin_user = User(
                email="admin@battlecard.com",
                full_name="System Administrator",
                hashed_password=get_password_hash("admin123!"),  # Change in production!
                role=UserRole.ADMIN,
                is_active=True
            )
            db.add(admin_user)
            db.commit()
            
            logger.info("Default admin user created", email=admin_user.email)
        
        db.close()
        
    except Exception as e:
        logger.error("Failed to initialize database", error=str(e))
        raise DatabaseError(
            message=f"Database initialization failed: {str(e)}",
            operation="initialization"
        )


class DatabaseTransaction:
    """Context manager for database transactions with proper error handling."""
    
    def __init__(self, db: Session):
        self.db = db
        self.committed = False
    
    def __enter__(self):
        return self.db
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is None and not self.committed:
            try:
                self.db.commit()
                self.committed = True
            except SQLAlchemyError as e:
                self.db.rollback()
                raise DatabaseError(
                    message=f"Transaction commit failed: {str(e)}",
                    operation="transaction_commit"
                )
        elif exc_type is not None:
            self.db.rollback()
            logger.error(
                "Transaction rolled back due to exception",
                exception_type=exc_type.__name__ if exc_type else None,
                exception_message=str(exc_val) if exc_val else None
            )
    
    def commit(self):
        """Explicitly commit the transaction."""
        try:
            self.db.commit()
            self.committed = True
        except SQLAlchemyError as e:
            self.db.rollback()
            raise DatabaseError(
                message=f"Transaction commit failed: {str(e)}",
                operation="explicit_commit"
            )


def with_transaction(db: Session):
    """Create a database transaction context manager."""
    return DatabaseTransaction(db)


# Database utilities
async def execute_raw_query(query: str, params: Dict[str, Any] = None) -> Any:
    """Execute raw SQL query safely with parameter binding."""
    try:
        db = SessionLocal()
        result = db.execute(text(query), params or {})
        
        if query.strip().upper().startswith('SELECT'):
            return result.fetchall()
        else:
            db.commit()
            return result.rowcount
            
    except SQLAlchemyError as e:
        logger.error("Raw query execution failed", query=query[:100], error=str(e))
        db.rollback()
        raise DatabaseError(
            message=f"Query execution failed: {str(e)}",
            operation="raw_query"
        )
    finally:
        db.close()


async def get_table_stats() -> Dict[str, Any]:
    """Get statistics about database tables."""
    try:
        db = SessionLocal()
        
        # Get table sizes and row counts
        stats_query = """
        SELECT 
            schemaname,
            tablename,
            attname,
            n_distinct,
            correlation
        FROM pg_stats 
        WHERE schemaname = 'public'
        ORDER BY tablename, attname;
        """
        
        result = db.execute(text(stats_query))
        stats = result.fetchall()
        
        # Get table sizes
        size_query = """
        SELECT 
            tablename,
            pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) as size
        FROM pg_tables 
        WHERE schemaname = 'public'
        ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;
        """
        
        result = db.execute(text(size_query))
        sizes = result.fetchall()
        
        db.close()
        
        return {
            "table_stats": [dict(row) for row in stats],
            "table_sizes": [dict(row) for row in sizes],
            "timestamp": time.time()
        }
        
    except Exception as e:
        logger.error("Failed to get table stats", error=str(e))
        return {"error": str(e), "timestamp": time.time()}