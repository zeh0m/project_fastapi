from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy.engine import URL

url = URL.create(
    drivername="postgresql",
    username="postgres",
    host="postgres",
    database="postgres",
    password="postgres"
)

engine = create_engine(url)

Sessionlocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)
Base = declarative_base()