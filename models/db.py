from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

DATABASE_NAME = "db.sqlite"

engine = create_engine(f"sqlite:///{DATABASE_NAME}", echo=False)
Session = sessionmaker(bind=engine)

Base = declarative_base()

def connect_db():
    session = Session()
    return session

def create_db():
    Base.metadata.create_all(engine)