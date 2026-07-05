from sqlalchemy import *
from sqlalchemy.orm import relation, sessionmaker, DeclarativeBase, Mapped, mapped_column

import json

# internal API imports
import account
import friends

# create engine
class Base(DeclarativeBase):
    pass

engine = create_engine('''"dbms://user:pwd@host/dbname''', echo=True)
Base.metadata.create_all(engine)

Session = sessionmaker(autocommit=False, autoflush=False, bind=engine)
session = Session()



def Update():
    '''TODO'''

def View():
    '''TODO'''