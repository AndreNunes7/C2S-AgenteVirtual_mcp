import os

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

load_dotenv()
DB_URL = os.getenv('DB_URL')

def connectDb(db_url=DB_URL):
    return create_engine(db_url)

# def sessao(engine):
#     Session = sessionmaker(bind=engine)
#     return Session()
