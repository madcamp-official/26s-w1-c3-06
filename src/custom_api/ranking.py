# external API imports
from sqlalchemy import *
from sqlalchemy.orm import relation, sessionmaker, DeclarativeBase, Mapped, mapped_column

from datetime import datetime
from zoneinfo import ZoneInfo

from flask import Flask, request, jsonify

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

# test required
class RankingEntry(Base): 
    __tablename__ = "User_Ranking"

    ID: Mapped[str] = mapped_column(primary_key=True)
    Return_Daily: Mapped[int] = mapped_column(Integer)

    __table_args__ = (
        ForeignKeyConstraint(["ID"], ["User_Info.ID"]),
    )

    # default profile is embedded in website
    def __init__(self, ID="", Return_Daily=0):
        self.ID = ID
        self.Return_Daily = Return_Daily
        
    def __repr__(self):
        return f"Ranking(ID: {self.ID}, Daily Return: {self.Return_Daily})"

Base.metadata.create_all(engine)

def Register(ID):
    user = session.get(UserAccount, ID)

    try:
        session.add(a1)
        session.commit()
    except:
        session.rollback()

# !! WIP !!
def Update():
    '''TODO'''

# !! WIP !!
def View():
    '''TODO'''

if __name__ == '__main__':
    app.run(debug=True, port=5000)