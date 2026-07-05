# external API imports

from sqlalchemy import *
from sqlalchemy.orm import relation, sessionmaker, DeclarativeBase, Mapped, mapped_column

from enum import Enum
from datetime import datetime
from zoneinfo import ZoneInfo

from flask import Flask, request, jsonify

# internal API imports
import account
import notify

# define custom types
class fnd_sts(Enum):
    REQUESTED = "REQUESTED"
    FRIENDS = "FRIENDS"
    UNRELATED = "UNRELATED"

# create engine
class Base(DeclarativeBase):
    pass

engine = create_engine('''"dbms://user:pwd@host/dbname''', echo=True)
Base.metadata.create_all(engine)

Session = sessionmaker(autocommit=False, autoflush=False, bind=engine)
session = Session()

# test required
class FriendEntry(Base):
    __tablename__ = "User_Friends"

    FromID: Mapped[str] = mapped_column(primary_key=True)
    ToID: Mapped[str] = mapped_column(primary_key=True)
    Friend_Date: Mapped[datetime] = mapped_column(Datetime(timezone=True), server_default=func.now())
    Friend_Status: Mapped[fnd_sts] = mapped_column()
    
    __table_args__ = (
        ForeignKeyConstraint(["FromID"], ["User_Info.ID"]),
        ForeignKeyConstraint(["ToID"], ["User_Info.ID"]),
    )

    def __init__(self, FromID="", ToID="", status=fnd_sts.REQUESTED):
        self.FromID = FromID
        self.ToID = ToID
        self.Friend_Date = datetime.now(ZoneInfo("Asia/Tokyo"))
        self.Friend_Status = status
        
    def __repr__(self):
        return f"Friend(SelfID: {self.FromID}, FriendID: {self.ToID}, Date: {self.Freind_Date} Status: {self.Friend_Status})"

Base.metadata.create_all(engine)

def Request():
    '''TODO'''

def View():
    '''TODO'''

def Delete():
    '''TODO'''

if __name__ == '__main__':
    app.run(debug=True, port=5000)