from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from ..core.config import settings

engine = create_engine(settings.SQLALCHEMY_DATABASE_URI, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# Import all models here so that Base has them registered:
from app.models.customer import Customer # noqa
# Add other models here, e.g.:
# from app.models.user import User # noqa
# from app.models.battlecard import Battlecard # noqa


# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close() 