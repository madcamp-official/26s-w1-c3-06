# external API imports
import os

from sqlalchemy import *
from sqlalchemy.orm import relationship, sessionmaker, DeclarativeBase, Mapped, mapped_column

from datetime import datetime
from zoneinfo import ZoneInfo
from decimal import Decimal

from flask import Flask, request, jsonify

app = Flask(__name__)

# internal API imports
import account
import friends
import stock

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
    # 그 시점의 User_Info.Non_Stock_Cash 스냅샷. 두 스냅샷 사이 Total_Asset 증감에서
    # 이 값의 증감을 빼면, 그 사이 며칠이 지났든 몇 번을 받았든 상관없이 순수 주식 손익만 남는다.
    Non_Stock_Cash: Mapped[int] = mapped_column(Integer, nullable=True)

    __table_args__ = (
        ForeignKeyConstraint(["ID"], ["User_Info.ID"]),
    )

    def __init__(self, Snapshot_Date=None, ID="", Total_Asset=0, Non_Stock_Cash=0):
        self.Snapshot_Date = Snapshot_Date
        self.ID = ID
        self.Total_Asset = Total_Asset
        self.Non_Stock_Cash = Non_Stock_Cash

    def __repr__(self):
        return f"Snapshot(Date: {self.Snapshot_Date}, ID: {self.ID}, Total_Asset: {self.Total_Asset})"

# ----------------------------------------------------------------------
# Core APIs
# ----------------------------------------------------------------------

def PrevSnapshot(user, today):
    ''' today보다 이전인 가장 최근 스냅샷(=어제 종가에 해당) '''
    return (
        session.query(DailySnapshot)
        .filter(DailySnapshot.ID == user.ID, DailySnapshot.Snapshot_Date < today)
        .order_by(DailySnapshot.Snapshot_Date.desc())
        .first()
    )

def EnsureTodaySnapshotAndReturn(user):
    ''' 오늘자 스냅샷(총자산 + 비거래성 현금 누계)을 현재 값으로 갱신하고, 직전 스냅샷 대비
    총자산 증감에서 그 사이 늘어난 비거래성 현금(퀴즈 보상 등)의 증감을 뺀 "순수 주식 손익"만
    User_Ranking에 반영한 뒤 그 값을 반환한다.

    "오늘 퀴즈를 받았는가"를 날짜 비교로 추론하지 않는다 — 퀴즈 보상이 Balance에 더해질 때마다
    Non_Stock_Cash도 함께 늘려두고(account.py), 그 누계값 자체를 비교하기 때문에 하루에 몇 번을
    받든 스냅샷을 언제/며칠 만에 다시 찍든 항상 정확하다. '''
    today = account.Midnight(datetime.now().astimezone())

    todaySnapshot = session.get(DailySnapshot, (today, user.ID))
    if not todaySnapshot:
        todaySnapshot = DailySnapshot(
            Snapshot_Date=today, ID=user.ID,
            Total_Asset=user.Balance, Non_Stock_Cash=user.Non_Stock_Cash,
        )
        session.add(todaySnapshot)
    else:
        # 하루 중 여러 번 조회될 수 있으므로, 오늘 스냅샷은 항상 최신 상태로 갱신해서
        # "오늘 하루" 증감이 조회 시점과 무관하게 최신 상태를 반영하게 한다.
        todaySnapshot.Total_Asset = user.Balance
        todaySnapshot.Non_Stock_Cash = user.Non_Stock_Cash
    session.commit()

    prevSnapshot = PrevSnapshot(user, today)
    if not prevSnapshot:
        stockDelta = 0
    else:
        rawDelta = todaySnapshot.Total_Asset - prevSnapshot.Total_Asset
        nonStockDelta = todaySnapshot.Non_Stock_Cash - prevSnapshot.Non_Stock_Cash
        stockDelta = rawDelta - nonStockDelta

    rankingEntry = session.get(RankingEntry, user.ID)
    if rankingEntry:
        rankingEntry.Return_Daily = stockDelta
    else:
        rankingEntry = RankingEntry(ID=user.ID, Return_Daily=stockDelta)
        session.add(rankingEntry)
    session.commit()

    return stockDelta

def ReturnPct(user, stockDelta):
    ''' 순수 주식 손익(원단위)을 어제 종가 총자산 대비 퍼센트로 환산한다. 소수점 4자리까지
    정밀도를 유지하고(다른 계산에 재사용할 수 있도록), 화면에 몇 자리를 보여줄지는
    프론트(social.js)가 정한다. '''
    today = account.Midnight(datetime.now().astimezone())
    prevSnapshot = PrevSnapshot(user, today)
    if not prevSnapshot or not prevSnapshot.Total_Asset:
        return 0.0
    return round(stockDelta / prevSnapshot.Total_Asset * 100, 4)

def CurrentStockReturn(user):
    '''현재 보유 중인 주식의 평가손익과 수익률을 계산한다.

    Balance/User_Ranking/Daily_Snapshot은 퀴즈 보상, 실현손익, 조회 시점에 따라
    현재 보유 주식의 평가 수익률과 어긋날 수 있으므로 소셜 랭킹은 보유 종목의
    평균매수가와 최신 현재가를 직접 비교한다.
    '''
    holdings = (
        account.session.query(account.AccountStock)
        .filter(account.AccountStock.ID == user.ID)
        .populate_existing()
        .all()
    )

    totalCost = Decimal("0")
    totalProfit = Decimal("0")

    for holding in holdings:
        quantity = holding.Own_Quantity or 0
        if quantity <= 0:
            continue

        avgPrice = Decimal(holding.Own_Avg or 0)
        costBasis = avgPrice * quantity
        if costBasis <= 0:
            continue

        currentPrice = stock.CurrentPrice(holding.Stock_Code)
        if currentPrice is None:
            currentPrice = avgPrice

        totalCost += costBasis
        totalProfit += (Decimal(currentPrice) - avgPrice) * quantity

    if totalCost <= 0:
        return 0, 0.0

    pct = round(float(totalProfit / totalCost * Decimal("100")), 4)
    return int(round(totalProfit)), pct

if __name__ == '__main__':
    app.run(debug=True, port=5000)
