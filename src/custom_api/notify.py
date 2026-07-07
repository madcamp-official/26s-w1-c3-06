from sqlalchemy import *
from sqlalchemy.orm import relationship, sessionmaker, DeclarativeBase, Mapped, mapped_column

# external API imports
from datetime import datetime
from zoneinfo import ZoneInfo

from flask import Flask, request, jsonify

app = Flask(__name__)

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
    Noti_Time: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    # default profile is embedded in website
    def __init__(self, Noti_Num=0, Noti_Head="",Noti_Body="",Noti_Time=None):
        self.Noti_Num=Noti_Num
        self.Noti_Head=Noti_Head
        self.Noti_Body=Noti_Body
        self.Noti_Time=Noti_Time
        
    def __repr__(self):
        return f"Notice(Number: {self.Noti_Num}, Head: {self.Noti_Head}, Body: {self.Noti_Body}, Date: {self.Noti_Time})"

Base.metadata.create_all(engine)

# !! WIP - 루트와 request 종류가 모두 일치할 시 한 함수만 존재할 수 있음 !!
@app.route('/home/notice')
def StockNotice():
    '''TODO'''

# !! WIP !!
@app.route('/home/notice')
def OrderNotice():
    
    return jsonify({
        "status": "success",
        "message": toUser.Nickname + "님에게 친구 요청을 받았습니다.",
        "notiNum": 1,
        "notiHead": "친구 추가 알림",
        "notiBody": toUser.Nickname + "님에게 친구 요청을 받았습니다.",
        "notiTime": datetime.now().astimezone(),
        "orderId": 1
    }), 200

# !! WIP !!
@app.route('/home/notice')
def FriendsNotice(fromId, toId, notiNum, notiTime):
    fromUser = session.scalars(
        select(account.UserAccount).where(account.UserAccount.ID == fromId)
    )
    toUser = session.scalars(
        select(account.UserAccount).where(account.UserAccount.ID == toId)
    )
    
    return jsonify({
        "status": "success",
        "message": toUser.Nickname + "님에게 친구 요청을 받았습니다.",
        "notiNum": 1,
        "notiHead": "친구 추가 알림",
        "notiBody": toUser.Nickname + "님에게 친구 요청을 받았습니다.",
        "notiTime": datetime.now().astimezone(),
        "fromId": fromId,
        "toId": toId
    }), 200

if __name__ == '__main__':
    app.run(debug=True, port=5000)