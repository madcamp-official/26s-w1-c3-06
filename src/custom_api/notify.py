from sqlalchemy import *
from sqlalchemy.orm import relation, sessionmaker, DeclarativeBase, Mapped, mapped_column

# external API imports
from datetime import datetime
from zoneinfo import ZoneInfo

from flask import Flask, request, jsonify

# internal API imports
import account
import stock
import order
import friends

# create engine
class Base(DeclarativeBase):
    pass

engine = create_engine('''"dbms://user:pwd@host/dbname''', echo=True)
Base.metadata.create_all(engine)

Session = sessionmaker(autocommit=False, autoflush=False, bind=engine)
session = Session()

# test required
class NoticeEntry(Base): 
    __tablename__ = "Notification"

    Noti_Num: Mapped[int] = mapped_column(Integer, primary_key=True)
    Noti_Head: Mapped[str] = mapped_column(Text)
    Noti_Body: Mapped[str] = mapped_column(Text)
    Noti_Time: Mapped[datetime] = mapped_column(Datetime(timezone=True), server_default=func.now())

    # default profile is embedded in website
    def __init__(self, Noti_Num=0, Noti_Head="",Noti_Body="",Noti_Time=None):
        self.Noti_Num=Noti_Num
        self.Noti_Head=Noti_Head
        self.Noti_Body=Noti_Body
        self.Noti_Time=Noti_Time
        
    def __repr__(self):
        return f"Notice(Number: {self.Noti_Num}, Head: {self.Noti_Head}, Body: {self.Noti_Body}, Date: {self.Noti_Time})"

Base.metadata.create_all(engine)

def StockNotice():
    '''TODO'''

def OrderNotice():
    '''TODO'''

def FriendsNotice():
    '''TODO'''

if __name__ == '__main__':
    app.run(debug=True, port=5000)