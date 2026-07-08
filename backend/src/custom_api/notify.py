# external API imports
import os

from sqlalchemy import *
from sqlalchemy.orm import relationship, sessionmaker, DeclarativeBase, Mapped, mapped_column

from datetime import datetime
from zoneinfo import ZoneInfo

from flask import Flask, request, jsonify

app = Flask(__name__)

# internal API imports
import account
import stock
import order

# create engine
class Base(DeclarativeBase):
    pass

DATABASE_URL = os.environ.get(
    "DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/mockinvest"
)

engine = create_engine(DATABASE_URL, echo=True)
Session = sessionmaker(autocommit=False, autoflush=False, bind=engine)
session = Session()

class NoticeEntry(Base):
    __tablename__ = "Notification"

    Noti_Num: Mapped[int] = mapped_column(Integer, primary_key=True)
    Noti_Head: Mapped[str] = mapped_column(Text)
    Noti_Body: Mapped[str] = mapped_column(Text)
    Noti_Time: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    def __init__(self, Noti_Num=0, Noti_Head="", Noti_Body="", Noti_Time=None):
        self.Noti_Num = Noti_Num
        self.Noti_Head = Noti_Head
        self.Noti_Body = Noti_Body
        self.Noti_Time = Noti_Time

    def __repr__(self):
        return f"Notice(Number: {self.Noti_Num}, Head: {self.Noti_Head}, Body: {self.Noti_Body}, Date: {self.Noti_Time})"

# 아래 세 링크 테이블은 Notification/User_Info/Stock_List/Stock_Order를 FK로 참조하지만,
# 이 프로젝트는 모듈마다 별도의 DeclarativeBase를 쓰고 있어(stock.py, order.py 등) 문자열 FK가
# 그 모듈들의 metadata 안에서는 풀리지 않는다. 실제 FK 제약은 이미 db/schema.sql에 있으므로,
# 여기서는 ForeignKeyConstraint 없이 순수 컬럼으로만 매핑한다 (mapper 설정 시점 에러 방지).
class FriendNotice(Base):
    __tablename__ = "Notification_Friends"

    Noti_Num: Mapped[int] = mapped_column(Integer, primary_key=True)
    FromID: Mapped[str] = mapped_column(String(16))
    ToID: Mapped[str] = mapped_column(String(16))

    def __init__(self, Noti_Num=0, FromID="", ToID=""):
        self.Noti_Num = Noti_Num
        self.FromID = FromID
        self.ToID = ToID

class OwnedNotice(Base):
    __tablename__ = "Notification_Owned"

    Noti_Num: Mapped[int] = mapped_column(Integer, primary_key=True)
    Stock_Code: Mapped[int] = mapped_column(Integer)

    def __init__(self, Noti_Num=0, Stock_Code=0):
        self.Noti_Num = Noti_Num
        self.Stock_Code = Stock_Code

class OrderNotice(Base):
    __tablename__ = "Notification_Order"

    Noti_Num: Mapped[int] = mapped_column(Integer, primary_key=True)
    Order_ID: Mapped[int] = mapped_column(Integer)

    def __init__(self, Noti_Num=0, Order_ID=0):
        self.Noti_Num = Noti_Num
        self.Order_ID = Order_ID

# ----------------------------------------------------------------------
# Helper Functions
# ----------------------------------------------------------------------

def NextNotiNum():
    return (session.query(func.coalesce(func.max(NoticeEntry.Noti_Num), 0)).scalar() or 0) + 1

# ----------------------------------------------------------------------
# Core APIs
# ----------------------------------------------------------------------

def NotifyFriendRequest(fromUser, toUser):
    ''' toUser에게 "OO님이 친구 요청을 보냈습니다" 알림을 만든다. friends.RequestFriend()에서 호출된다. '''
    notiNum = NextNotiNum()
    notice = NoticeEntry(
        Noti_Num=notiNum,
        Noti_Head="친구 추가 알림",
        Noti_Body=f"{fromUser.Nickname}님이 친구 요청을 보냈습니다.",
        Noti_Time=datetime.now().astimezone(),
    )
    session.add(notice)
    session.flush()  # FriendNotice.Noti_Num이 참조할 Notification 행을 먼저 실제로 insert해둔다
    session.add(FriendNotice(Noti_Num=notiNum, FromID=fromUser.ID, ToID=toUser.ID))
    session.commit()
    return notice

def NotifyOrderFilled(orderEntry, stockName):
    ''' 주문이 체결됐을 때 주문을 넣은 사람에게 알림을 만든다.
    !! 아직 어디서도 호출되지 않는다 !! order.py의 주문 체결 로직이 구현되면 그 안에서 호출해야 한다. '''
    posLabel = "매수" if str(orderEntry.Order_Position).endswith("BTO") else "매도"
    notiNum = NextNotiNum()
    notice = NoticeEntry(
        Noti_Num=notiNum,
        Noti_Head="주문 체결 알림",
        Noti_Body=f"{stockName} {orderEntry.Order_Quantity}주 {posLabel}가 체결됐어요",
        Noti_Time=datetime.now().astimezone(),
    )
    session.add(notice)
    session.flush()
    session.add(OrderNotice(Noti_Num=notiNum, Order_ID=orderEntry.Order_ID))
    session.commit()
    return notice

def NotifyStockMove(stockCode, stockName, changePct):
    ''' 특정 종목을 보유한 모든 사용자에게 "오늘 X% 올랐어요/내렸어요" 알림을 만든다.
    !! 아직 어디서도 호출되지 않는다 !! 실시간/일별 시세 갱신 파이프라인이 아직 없어서 호출할 곳이 없다.
    주의: 이 알림은 Noti_Num 하나를 그 종목을 보유한 모든 사용자가 공유한다. 이 프로젝트 스키마에는
    사용자별 "읽음/삭제" 상태를 저장하는 테이블이 없어서, 한 명이 삭제하면 전원에게서 사라진다. '''
    sign = "올랐어요" if changePct >= 0 else "내렸어요"
    notiNum = NextNotiNum()
    notice = NoticeEntry(
        Noti_Num=notiNum,
        Noti_Head="보유 종목 알림",
        Noti_Body=f"{stockName}, 오늘 {abs(changePct):.1f}% {sign}",
        Noti_Time=datetime.now().astimezone(),
    )
    session.add(notice)
    session.flush()
    session.add(OwnedNotice(Noti_Num=notiNum, Stock_Code=stockCode))
    session.commit()
    return notice

def ListNotifications(userId):
    ''' userId가 수신자인 알림을 세 종류(친구/주문/보유종목) 다 모아서 최신순으로 반환한다 '''
    results = []

    friendRows = (
        session.query(NoticeEntry)
        .join(FriendNotice, FriendNotice.Noti_Num == NoticeEntry.Noti_Num)
        .filter(FriendNotice.ToID == userId)
        .all()
    )
    for notice in friendRows:
        results.append({
            "id": notice.Noti_Num,
            "type": "friend",
            "title": notice.Noti_Body,
            "time": notice.Noti_Time,
        })

    orderRows = (
        session.query(NoticeEntry)
        .join(OrderNotice, OrderNotice.Noti_Num == NoticeEntry.Noti_Num)
        .join(order.OrderEntry, order.OrderEntry.Order_ID == OrderNotice.Order_ID)
        .filter(order.OrderEntry.ID == userId)
        .all()
    )
    for notice in orderRows:
        results.append({
            "id": notice.Noti_Num,
            "type": "order",
            "title": notice.Noti_Body,
            "time": notice.Noti_Time,
        })

    ownedRows = (
        session.query(NoticeEntry, stock.StockEntry.Stock_Name)
        .join(OwnedNotice, OwnedNotice.Noti_Num == NoticeEntry.Noti_Num)
        .join(account.AccountStock, account.AccountStock.Stock_Code == OwnedNotice.Stock_Code)
        .join(stock.StockEntry, stock.StockEntry.Stock_Code == OwnedNotice.Stock_Code)
        .filter(account.AccountStock.ID == userId)
        .all()
    )
    for notice, stockName in ownedRows:
        results.append({
            "id": notice.Noti_Num,
            "type": "owned",
            "title": notice.Noti_Body,
            "time": notice.Noti_Time,
            "related_name": stockName,
        })

    results.sort(key=lambda n: n["time"], reverse=True)
    for n in results:
        n["time"] = n["time"].isoformat()
    return results

def DeleteNotification(notiNum, userId):
    ''' userId가 실제 수신자인 경우에만 삭제한다 (알림 번호를 추측해서 남의 알림을 지우는 것 방지).
    보유종목 알림처럼 여러 명이 같은 Noti_Num을 공유하는 경우, 삭제하면 그 알림을 보던 다른 사용자
    화면에서도 사라진다 (사용자별 읽음 상태 테이블이 없어서 생기는 한계). '''
    belongsToUser = (
        session.query(FriendNotice)
        .filter(FriendNotice.Noti_Num == notiNum, FriendNotice.ToID == userId).first()
        or session.query(OrderNotice)
        .join(order.OrderEntry, order.OrderEntry.Order_ID == OrderNotice.Order_ID)
        .filter(OrderNotice.Noti_Num == notiNum, order.OrderEntry.ID == userId).first()
        or session.query(OwnedNotice)
        .join(account.AccountStock, account.AccountStock.Stock_Code == OwnedNotice.Stock_Code)
        .filter(OwnedNotice.Noti_Num == notiNum, account.AccountStock.ID == userId).first()
    )
    if not belongsToUser:
        return False

    session.query(FriendNotice).filter(FriendNotice.Noti_Num == notiNum).delete()
    session.query(OrderNotice).filter(OrderNotice.Noti_Num == notiNum).delete()
    session.query(OwnedNotice).filter(OwnedNotice.Noti_Num == notiNum).delete()
    session.query(NoticeEntry).filter(NoticeEntry.Noti_Num == notiNum).delete()
    session.commit()
    return True

if __name__ == '__main__':
    app.run(debug=True, port=5000)
