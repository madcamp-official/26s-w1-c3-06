# external API imports
from sqlalchemy import *
from sqlalchemy.orm import relationship, sessionmaker, DeclarativeBase, Mapped, mapped_column

from datetime import datetime
from zoneinfo import ZoneInfo

from flask import Flask, request, jsonify

app = Flask(__name__)

# internal API imports
import account
import stock

# create engine
class Base(DeclarativeBase):
    pass

# 이 모듈만의 별도 세션(별도 커넥션/트랜잭션)을 두면, order.py가 같은 요청 안에서 이미 flush해둔
# (아직 커밋 전인) Stock_Order 행이 그 세션에서는 안 보여서 FK 위반이 난다 (서로 다른 트랜잭션이라
# 상대방의 커밋 전 변경은 못 봄). 그래서 함수 안에서 항상 account.session을 직접 참조해서 쓴다
# (모듈 최상단에서 "session = account.session"으로 별칭을 만들면, 순환 import 도중 account.py가
# 아직 session을 만들기 전 시점이라 AttributeError가 난다 - 그래서 참조를 함수 호출 시점까지 미룬다).

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

# (Noti_Num, ID) 복합키다: 같은 종목을 보유한 사람이 여럿이면 Noti_Num 하나에 수신자 수만큼
# 행이 생긴다. 그래야 한 사람이 지워도 (Noti_Num, 그 사람 ID) 행만 없어지고 다른 수신자는 그대로 본다.
class OwnedNotice(Base):
    __tablename__ = "Notification_Owned"

    Noti_Num: Mapped[int] = mapped_column(Integer, primary_key=True)
    ID: Mapped[str] = mapped_column(String(16), primary_key=True)
    Stock_Code: Mapped[int] = mapped_column(Integer)

    def __init__(self, Noti_Num=0, ID="", Stock_Code=0):
        self.Noti_Num = Noti_Num
        self.ID = ID
        self.Stock_Code = Stock_Code

# 주문 알림은 수신자가 항상 한 명(주문한 사람)이지만, OwnedNotice와 같은 (Noti_Num, ID) 모양으로
# 맞춰서 Stock_Order까지 조인하지 않고 바로 수신자를 알 수 있게 한다.
class OrderNotice(Base):
    __tablename__ = "Notification_Order"

    Noti_Num: Mapped[int] = mapped_column(Integer, primary_key=True)
    ID: Mapped[str] = mapped_column(String(16), primary_key=True)
    Order_ID: Mapped[int] = mapped_column(Integer)

    def __init__(self, Noti_Num=0, ID="", Order_ID=0):
        self.Noti_Num = Noti_Num
        self.ID = ID
        self.Order_ID = Order_ID

# ----------------------------------------------------------------------
# Helper Functions
# ----------------------------------------------------------------------

def NextNotiNum():
    return (account.session.query(func.coalesce(func.max(NoticeEntry.Noti_Num), 0)).scalar() or 0) + 1

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
    account.session.add(notice)
    account.session.flush()  # FriendNotice.Noti_Num이 참조할 Notification 행을 먼저 실제로 insert해둔다
    account.session.add(FriendNotice(Noti_Num=notiNum, FromID=fromUser.ID, ToID=toUser.ID))
    account.session.commit()
    return notice

def NotifyOrderFilled(orderEntry, stockName):
    ''' 주문이 체결됐을 때 주문을 넣은 사람에게 알림을 만든다. order.ExecuteOrder()에서 호출된다.
    order.py도 account.session을 쓰기 때문에, 여기서 만드는 Notification_Order가 참조하는
    Stock_Order 행(같은 요청 안에서 방금 flush됨)이 같은 트랜잭션 안에서 바로 보인다. '''
    posLabel = "매수" if str(orderEntry.Order_Position).endswith("BTO") else "매도"
    notiNum = NextNotiNum()
    notice = NoticeEntry(
        Noti_Num=notiNum,
        Noti_Head="주문 체결 알림",
        Noti_Body=f"{stockName} {orderEntry.Order_Quantity}주 {posLabel}가 체결됐어요",
        Noti_Time=datetime.now().astimezone(),
    )
    account.session.add(notice)
    account.session.flush()  # OrderNotice.Noti_Num이 참조할 Notification 행을 먼저 실제로 insert해둔다
    account.session.add(OrderNotice(Noti_Num=notiNum, ID=orderEntry.ID, Order_ID=orderEntry.Order_ID))
    account.session.commit()
    return notice

def NotifyStockMove(stockCode, stockName, changePct):
    ''' 특정 종목을 보유한 모든 사용자 각각에게 "오늘 X% 올랐어요/내렸어요" 알림을 만든다.
    !! 아직 어디서도 호출되지 않는다 !! "몇 % 움직이면 알릴지"를 판단하는 트리거가 아직 없어서
    (price_generator.py는 그냥 계속 틱만 만들 뿐 임계값 감지를 안 한다) 호출할 곳이 없다.
    수신자마다 (Noti_Num, ID) 행을 하나씩 만들기 때문에, 한 사람이 삭제해도 같은 종목을 보유한
    다른 사람 화면에서는 그대로 남아있다. '''
    holderIds = [
        row[0] for row in
        account.session.query(account.AccountStock.ID)
        .filter(account.AccountStock.Stock_Code == stockCode)
        .distinct()
        .all()
    ]
    if not holderIds:
        return None

    sign = "올랐어요" if changePct >= 0 else "내렸어요"
    notiNum = NextNotiNum()
    notice = NoticeEntry(
        Noti_Num=notiNum,
        Noti_Head="보유 종목 알림",
        Noti_Body=f"{stockName}, 오늘 {abs(changePct):.1f}% {sign}",
        Noti_Time=datetime.now().astimezone(),
    )
    account.session.add(notice)
    account.session.flush()
    for holderId in holderIds:
        account.session.add(OwnedNotice(Noti_Num=notiNum, ID=holderId, Stock_Code=stockCode))
    account.session.commit()
    return notice

def ListNotifications(userId):
    ''' userId가 수신자인 알림을 세 종류(친구/주문/보유종목) 다 모아서 최신순으로 반환한다 '''
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

    # OwnedNotice.ID로 바로 거르기 때문에, 알림을 받은 뒤 그 종목을 팔았어도(=지금은
    # AccountStock에 없어도) 알림은 그대로 남는다 (예전엔 AccountStock과 조인해서, 팔면
    # 알림이 같이 사라지는 부작용이 있었다).
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
    for n in results:
        n["time"] = n["time"].isoformat()
    return results

def DeleteNotification(notiNum, userId):
    ''' userId 몫의 수신 행만 지운다 (알림 번호를 추측해서 남의 알림을 지우는 것 방지).
    OwnedNotice/OrderNotice가 이제 (Noti_Num, ID) 단위라, 같은 알림을 여러 명이 받았어도
    이 사용자 행만 없어지고 다른 수신자에게는 그대로 남는다. 아무도 더 참조하지 않게 되면
    그때 공유 Notification 원본도 같이 정리한다. '''
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

    stillReferenced = (
        account.session.query(FriendNotice).filter(FriendNotice.Noti_Num == notiNum).first()
        or account.session.query(OrderNotice).filter(OrderNotice.Noti_Num == notiNum).first()
        or account.session.query(OwnedNotice).filter(OwnedNotice.Noti_Num == notiNum).first()
    )
    if not stillReferenced:
        account.session.query(NoticeEntry).filter(NoticeEntry.Noti_Num == notiNum).delete()

    account.session.commit()
    return True

if __name__ == '__main__':
    app.run(debug=True, port=5000)
