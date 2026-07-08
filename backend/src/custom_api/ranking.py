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
import friends

# User_Info(계좌)를 FK로 참조하는 모델(RankingEntry, DailySnapshot)이 있어서, 같은 metadata를 쓰도록
# account.py의 Base를 그대로 공유한다 (독자적인 Base를 쓰면 FK 문자열 "User_Info.ID"가 이 모듈의
# metadata 안에서는 찾아지지 않아 NoReferencedTableError가 난다).
from account import Base

DATABASE_URL = os.environ.get(
    "DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/mockinvest"
)

engine = create_engine(DATABASE_URL, echo=True)
Session = sessionmaker(autocommit=False, autoflush=False, bind=engine)
session = Session()

class RankingEntry(Base):
    __tablename__ = "User_Ranking"

    ID: Mapped[str] = mapped_column(primary_key=True)
    Return_Daily: Mapped[int] = mapped_column(Integer)

    __table_args__ = (
        ForeignKeyConstraint(["ID"], ["User_Info.ID"]),
    )

    def __init__(self, ID="", Return_Daily=0):
        self.ID = ID
        self.Return_Daily = Return_Daily

    def __repr__(self):
        return f"Ranking(ID: {self.ID}, Daily Return: {self.Return_Daily})"

class DailySnapshot(Base):
    __tablename__ = "Daily_Snapshot"

    Snapshot_Date: Mapped[datetime] = mapped_column(DateTime(timezone=True), primary_key=True)
    ID: Mapped[str] = mapped_column(String(16), primary_key=True)
    Total_Asset: Mapped[int] = mapped_column(Integer, nullable=True)

    __table_args__ = (
        ForeignKeyConstraint(["ID"], ["User_Info.ID"]),
    )

    def __init__(self, Snapshot_Date=None, ID="", Total_Asset=0):
        self.Snapshot_Date = Snapshot_Date
        self.ID = ID
        self.Total_Asset = Total_Asset

    def __repr__(self):
        return f"Snapshot(Date: {self.Snapshot_Date}, ID: {self.ID}, Total_Asset: {self.Total_Asset})"

# ----------------------------------------------------------------------
# Core APIs
# ----------------------------------------------------------------------

def EnsureTodaySnapshotAndReturn(user):
    ''' 오늘자 스냅샷을 없으면 만들고, 직전 스냅샷 대비 원단위 증감을 User_Ranking에 반영한 뒤 그 증감값을 반환한다 '''
    today = account.Midnight(datetime.now().astimezone())

    todaySnapshot = session.get(DailySnapshot, (today, user.ID))
    if not todaySnapshot:
        todaySnapshot = DailySnapshot(Snapshot_Date=today, ID=user.ID, Total_Asset=user.Balance)
        session.add(todaySnapshot)
        session.commit()

    prevSnapshot = (
        session.query(DailySnapshot)
        .filter(DailySnapshot.ID == user.ID, DailySnapshot.Snapshot_Date < today)
        .order_by(DailySnapshot.Snapshot_Date.desc())
        .first()
    )
    wonDelta = (todaySnapshot.Total_Asset - prevSnapshot.Total_Asset) if prevSnapshot else 0

    rankingEntry = session.get(RankingEntry, user.ID)
    if rankingEntry:
        rankingEntry.Return_Daily = wonDelta
    else:
        rankingEntry = RankingEntry(ID=user.ID, Return_Daily=wonDelta)
        session.add(rankingEntry)
    session.commit()

    return wonDelta

def ReturnPct(user, wonDelta):
    ''' 원단위 증감을 직전 총자산 대비 퍼센트(소수점 첫째자리)로 환산한다 '''
    prevTotal = user.Balance - wonDelta
    if not prevTotal:
        return 0.0
    return round(wonDelta / prevTotal * 100, 1)

if __name__ == '__main__':
    app.run(debug=True, port=5000)