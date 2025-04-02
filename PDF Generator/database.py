from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker


URL = "sqlite:///pdf.db"

Engine = create_engine(url=URL, connect_args={"check_same_thread": True})

Session = sessionmaker(autoflush=False, autocommit=False, bind=Engine)

Base = declarative_base()


def get_db():
    db = Session()

    try:
        yield db
    finally:
        db.close

        