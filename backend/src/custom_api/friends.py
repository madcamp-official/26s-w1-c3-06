# external API imports
import os

from sqlalchemy import *
from sqlalchemy.orm import relationship, sessionmaker, DeclarativeBase, Mapped, mapped_column

from enum import Enum
from datetime import datetime
from zoneinfo import ZoneInfo

from flask import Flask, request, jsonify

app = Flask(__name__)

# internal API imports
import account
import notify

# define custom types
class fnd_sts(Enum):
    REQUESTED = "REQUESTED"
    FRIENDS = "FRIENDS"
    UNRELATED = "UNRELATED"

# User_Info(계좌)를 FK로 참조하는 FriendEntry가 있어서, 같은 metadata를 쓰도록 account.py의 Base를
# 그대로 공유한다 (독자적인 Base를 쓰면 FK 문자열 "User_Info.ID"가 이 모듈의 metadata 안에서는
# 찾아지지 않아 NoReferencedTableError가 난다).
from account import Base

DATABASE_URL = os.environ.get(
    "DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/mockinvest"
)

engine = create_engine(DATABASE_URL, echo=True)
Session = sessionmaker(autocommit=False, autoflush=False, bind=engine)
session = Session()

# ----------------------------------------------------------------------
# Core APIs 
# ----------------------------------------------------------------------

# test required
class FriendEntry(Base):
    __tablename__ = "User_Friends"

    FromID: Mapped[str] = mapped_column(primary_key=True)
    ToID: Mapped[str] = mapped_column(primary_key=True)
    Friend_Date: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    Friend_Status: Mapped[fnd_sts] = mapped_column()
    
    __table_args__ = (
        ForeignKeyConstraint(["FromID"], ["User_Info.ID"]),
        ForeignKeyConstraint(["ToID"], ["User_Info.ID"]),
    )

    def __init__(self, FromID="", ToID="", status=fnd_sts.REQUESTED):
        self.FromID = FromID
        self.ToID = ToID
        self.Friend_Date = datetime.now().astimezone()
        self.Friend_Status = status
        
    def __repr__(self):
        return f"Friend(SelfID: {self.FromID}, FriendID: {self.ToID}, Date: {self.Friend_Date} Status: {self.Friend_Status})"

# test required
def RequestFriend(fromId, toId):
    ''' 친구 요청 row(REQUESTED)를 만든다. 이미 친구/이미 요청됨이면 막는다.
    반환: (FriendEntry|None, message, toNickname|None) '''
    fromUser = session.get(account.UserAccount, fromId)
    toUser = session.get(account.UserAccount, toId)

    if not fromUser:
        return None, "사용자를 찾지 못했습니다. 다시 로그인해 주세요.", None
    if not toUser:
        return None, "친구 추가를 요청할 사용자를 찾지 못했습니다.", None
    if fromId == toId:
        return None, "자기 자신에게는 친구 요청을 보낼 수 없습니다.", None

    existing = (
        session.query(FriendEntry)
        .filter(or_(
            and_(FriendEntry.FromID == fromId, FriendEntry.ToID == toId),
            and_(FriendEntry.FromID == toId, FriendEntry.ToID == fromId),
        ))
        .first()
    )
    if existing and existing.Friend_Status == fnd_sts.FRIENDS:
        return None, "이미 친구입니다.", None
    if existing and existing.Friend_Status == fnd_sts.REQUESTED:
        return None, "이미 친구 요청을 보냈습니다.", None

    entry = FriendEntry(FromID=fromId, ToID=toId, status=fnd_sts.REQUESTED)
    session.add(entry)
    session.commit()
    return entry, toUser.Nickname + "님에게 친구 요청을 전송했습니다.", toUser.Nickname

# test required
def AcceptFriend(fromId, toId):
    ''' toId(수락하는 사람)가 fromId(요청 보낸 사람)의 REQUESTED 요청을 FRIENDS로 바꾼다 '''
    entry = (
        session.query(FriendEntry)
        .filter(FriendEntry.FromID == fromId, FriendEntry.ToID == toId, FriendEntry.Friend_Status == fnd_sts.REQUESTED)
        .first()
    )
    if not entry:
        return False, "수락할 친구 요청을 찾지 못했습니다."

    entry.Friend_Status = fnd_sts.FRIENDS
    session.commit()
    return True, "친구가 되었습니다."

# test required
def GetFriendIds(userId):
    ''' FRIENDS 상태인 상대방 ID 목록 (내가 FromID든 ToID든 상관없이) '''
    rows = (
        session.query(FriendEntry)
        .filter(
            FriendEntry.Friend_Status == fnd_sts.FRIENDS,
            or_(FriendEntry.FromID == userId, FriendEntry.ToID == userId),
        )
        .all()
    )
    return [row.ToID if row.FromID == userId else row.FromID for row in rows]

# test required
def GetPendingRequest(userId):
    ''' 나(userId)에게 온 미처리 요청 중 가장 최근 1건. 없으면 None '''
    return (
        session.query(FriendEntry)
        .filter(FriendEntry.ToID == userId, FriendEntry.Friend_Status == fnd_sts.REQUESTED)
        .order_by(FriendEntry.Friend_Date.desc())
        .first()
    )

# test required
def DeleteFriend(fromId, toId):
    ''' 친구(FRIENDS) 삭제와 요청(REQUESTED) 거절을 모두 처리한다. 양방향으로 매치. '''
    stmt = delete(FriendEntry).where(or_(
        and_(FriendEntry.FromID == fromId, FriendEntry.ToID == toId),
        and_(FriendEntry.FromID == toId, FriendEntry.ToID == fromId),
    ))
    result = session.execute(stmt)
    session.commit()
    return result.rowcount > 0

if __name__ == '__main__':
    app.run(debug=True, port=5000)