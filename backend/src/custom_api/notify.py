from datetime import datetime

from flask import Flask
from sqlalchemy import DateTime, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

import account
import stock
from account import Base

app = Flask(__name__)


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
        return f"Notice(Number: {self.Noti_Num}, Head: {self.Noti_Head})"


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
    ID: Mapped[str] = mapped_column(String(16), primary_key=True)
    Stock_Code: Mapped[int] = mapped_column(Integer)

    def __init__(self, Noti_Num=0, ID="", Stock_Code=0):
        self.Noti_Num = Noti_Num
        self.ID = ID
        self.Stock_Code = Stock_Code


class OrderNotice(Base):
    __tablename__ = "Notification_Order"

    Noti_Num: Mapped[int] = mapped_column(Integer, primary_key=True)
    ID: Mapped[str] = mapped_column(String(16), primary_key=True)
    Order_ID: Mapped[int] = mapped_column(Integer)

    def __init__(self, Noti_Num=0, ID="", Order_ID=0):
        self.Noti_Num = Noti_Num
        self.ID = ID
        self.Order_ID = Order_ID


def _session(db_session=None):
    return db_session or account.session


def NextNotiNum(db_session=None):
    session = _session(db_session)
    return (session.query(func.coalesce(func.max(NoticeEntry.Noti_Num), 0)).scalar() or 0) + 1


def NotifyFriendRequest(fromUser, toUser, db_session=None):
    session = _session(db_session)
    notiNum = NextNotiNum(session)
    notice = NoticeEntry(
        Noti_Num=notiNum,
        Noti_Head="친구 추가 알림",
        Noti_Body=f"{fromUser.Nickname}님이 친구 요청을 보냈습니다.",
        Noti_Time=datetime.now().astimezone(),
    )
    session.add(notice)
    session.flush()
    session.add(FriendNotice(Noti_Num=notiNum, FromID=fromUser.ID, ToID=toUser.ID))
    if db_session is None:
        session.commit()
    return notice


def NotifyOrderFilled(orderEntry, stockName, db_session=None):
    session = _session(db_session)
    posLabel = "매수" if str(orderEntry.Order_Position).endswith("BTO") else "매도"
    notiNum = NextNotiNum(session)
    notice = NoticeEntry(
        Noti_Num=notiNum,
        Noti_Head="주문 체결 알림",
        Noti_Body=f"{stockName} {orderEntry.Order_Quantity}주 {posLabel}가 체결되었습니다.",
        Noti_Time=datetime.now().astimezone(),
    )
    session.add(notice)
    session.flush()
    session.add(OrderNotice(Noti_Num=notiNum, ID=orderEntry.ID, Order_ID=orderEntry.Order_ID))
    if db_session is None:
        session.commit()
    return notice


def NotifyStockMove(stockCode, stockName, changePct, db_session=None):
    session = _session(db_session)
    holderIds = [
        row[0]
        for row in session.query(account.AccountStock.ID)
        .filter(account.AccountStock.Stock_Code == stockCode)
        .distinct()
        .all()
    ]
    if not holderIds:
        return None

    today = datetime.now().astimezone().date()
    alreadySent = (
        session.query(OwnedNotice)
        .join(NoticeEntry, NoticeEntry.Noti_Num == OwnedNotice.Noti_Num)
        .filter(
            OwnedNotice.Stock_Code == stockCode,
            func.date(NoticeEntry.Noti_Time) == today,
        )
        .first()
    )
    if alreadySent:
        return None

    direction = "올랐어요" if changePct >= 0 else "내렸어요"
    notiNum = NextNotiNum(session)
    notice = NoticeEntry(
        Noti_Num=notiNum,
        Noti_Head="보유 종목 알림",
        Noti_Body=f"{stockName}, 오늘 {abs(changePct):.1f}% {direction}.",
        Noti_Time=datetime.now().astimezone(),
    )
    session.add(notice)
    session.flush()
    for holderId in holderIds:
        session.add(OwnedNotice(Noti_Num=notiNum, ID=holderId, Stock_Code=stockCode))
    if db_session is None:
        session.commit()
    return notice


def ListNotifications(userId):
    results = []

    friendRows = (
        account.session.query(NoticeEntry)
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
        account.session.query(NoticeEntry)
        .join(OrderNotice, OrderNotice.Noti_Num == NoticeEntry.Noti_Num)
        .filter(OrderNotice.ID == userId)
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
        account.session.query(NoticeEntry, stock.StockEntry.Stock_Name)
        .join(OwnedNotice, OwnedNotice.Noti_Num == NoticeEntry.Noti_Num)
        .join(stock.StockEntry, stock.StockEntry.Stock_Code == OwnedNotice.Stock_Code)
        .filter(OwnedNotice.ID == userId)
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
    for notification in results:
        notification["time"] = notification["time"].isoformat()
    return results


def DeleteNotification(notiNum, userId):
    friendRow = account.session.query(FriendNotice).filter(
        FriendNotice.Noti_Num == notiNum, FriendNotice.ToID == userId
    ).first()
    orderRow = account.session.query(OrderNotice).filter(
        OrderNotice.Noti_Num == notiNum, OrderNotice.ID == userId
    ).first()
    ownedRow = account.session.query(OwnedNotice).filter(
        OwnedNotice.Noti_Num == notiNum, OwnedNotice.ID == userId
    ).first()

    if not (friendRow or orderRow or ownedRow):
        return False

    if friendRow:
        account.session.delete(friendRow)
    if orderRow:
        account.session.delete(orderRow)
    if ownedRow:
        account.session.delete(ownedRow)

    account.session.flush()
    stillReferenced = (
        account.session.query(FriendNotice).filter(FriendNotice.Noti_Num == notiNum).first()
        or account.session.query(OrderNotice).filter(OrderNotice.Noti_Num == notiNum).first()
        or account.session.query(OwnedNotice).filter(OwnedNotice.Noti_Num == notiNum).first()
    )
    if not stillReferenced:
        account.session.query(NoticeEntry).filter(NoticeEntry.Noti_Num == notiNum).delete()

    account.session.commit()
    return True


if __name__ == "__main__":
    app.run(debug=True, port=5000)
