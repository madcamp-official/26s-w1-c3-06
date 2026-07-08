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
import order
import news

from account import Base

DATABASE_URL = os.environ.get(
    "DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/mockinvest"
)

engine = create_engine(DATABASE_URL, echo=True)
Session = sessionmaker(autocommit=False, autoflush=False, bind=engine)
session = Session()

# test required
class StockEntry(Base):
    __tablename__ = "Stock_List"

    Stock_Code: Mapped[int] = mapped_column(Integer, primary_key=True)
    Stock_Name: Mapped[str] = mapped_column(String(20))
    Stock_Logo: Mapped[bytes] = mapped_column(LargeBinary)
    Stock_Desc: Mapped[str] = mapped_column(Text, nullable=True)

    def __init__(self, Stock_Code, Stock_Name="", Stock_Logo=None, Stock_Desc=None):
        self.Stock_Code = Stock_Code
        self.Stock_Name = Stock_Name
        self.Stock_Logo = Stock_Logo
        self.Stock_Desc = Stock_Desc

    def __repr__(self):
        return f"Stock(Code: {self.Stock_Code}, Name: {self.Stock_Name}, Desc: {self.Stock_Desc})"

# test required
class StockPriceEntry(Base):
    __tablename__ = "Stock_DailyPrice"

    Trade_Date: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), primary_key=True)
    Stock_Code: Mapped[int] = mapped_column(primary_key=True)
    Open: Mapped[int] = mapped_column(Integer)
    High: Mapped[int] = mapped_column(Integer)
    Low: Mapped[int] = mapped_column(Integer)
    Close: Mapped[int] = mapped_column(Integer)
    Volume: Mapped[int] = mapped_column(Integer)

    __table_args__ = (
        ForeignKeyConstraint(["Stock_Code"], ["Stock_List.Stock_Code"]),
    )

    # default profile is embedded in website
    def __init__(self, Trade_Date, Stock_Code, Open=0, High=0, Low=0, Close=0, Volume=0):
        self.Trade_Date = Trade_Date
        self.Stock_Code = Stock_Code
        self.Open = Open
        self.High = High
        self.Low = Low
        self.Close = Close
        self.Volume = Volume

    def __repr__(self):
        return f"StockPrice(Date: {self.Trade_Date}, Code: {self.Stock_Code}, High: {self.High}, Low: {self.Low}, Open: {self.Open}, Close: {self.Close})"

# price_generator.py가 종목별로 GBM 시세를 생성할 때 쓰는 파라미터. Mu/Sigma/R은 연 단위.
class StockParams(Base):
    __tablename__ = "Stock_Params"

    Stock_Code: Mapped[int] = mapped_column(Integer, primary_key=True)
    Mu: Mapped[float] = mapped_column(Numeric(10, 6))
    Sigma: Mapped[float] = mapped_column(Numeric(10, 6))
    R: Mapped[float] = mapped_column(Numeric(10, 6))
    K: Mapped[float] = mapped_column(Numeric(14, 2))

    def __init__(self, Stock_Code=0, Mu=0.05, Sigma=0.25, R=0.035, K=0):
        self.Stock_Code = Stock_Code
        self.Mu = Mu
        self.Sigma = Sigma
        self.R = R
        self.K = K

    def __repr__(self):
        return f"StockParams(Code: {self.Stock_Code}, Mu: {self.Mu}, Sigma: {self.Sigma}, R: {self.R}, K: {self.K})"

# Database tables will be created when the Flask app starts
# Base.metadata.create_all(engine)

# ----------------------------------------------------------------------
# Core APIs
# ----------------------------------------------------------------------
# 실제 HTTP 라우트는 이 모듈이 아니라 account.py의 account.app에 등록한다 (이 모듈의 app은
# main.py에서 실행되지 않는 인스턴스라 여기 등록해봐야 호출되지 않는다). 이 파일은 순수 헬퍼만 둔다.

def LatestPrices(stockCode, limit=2):
    ''' 최근 거래일 종가부터 최신순으로 limit개 반환 (오늘, 어제, ...).
    account.session은 요청 전반에 걸쳐 재사용되는 전역 세션이라, 이미 identity map에 올라와 있는
    행은 populate_existing() 없이는 DB에 새로 쓰인 값 대신 예전에 로드했던 값을 그대로 돌려줄 수
    있다 (price_generator.py는 별도 프로세스에서 계속 갱신 중이므로 이 캐시가 특히 위험하다).
    그래서 매번 DB의 최신 값으로 강제로 덮어써서, 주문 체결 시 항상 마지막 틱 가격을 쓰게 한다. '''
    return (
        account.session.query(StockPriceEntry)
        .filter(StockPriceEntry.Stock_Code == stockCode)
        .order_by(StockPriceEntry.Trade_Date.desc())
        .limit(limit)
        .populate_existing()
        .all()
    )

def CurrentPrice(stockCode):
    ''' 가장 최근 종가(=오늘 마지막으로 생성된 틱의 가격)를 현재가로 취급한다. 시세 데이터가 없으면 None. '''
    latest = LatestPrices(stockCode, limit=1)
    return latest[0].Close if latest else None

def TodayRow(stockCode):
    ''' 오늘(=가장 최근 Trade_Date) 행. price_generator.py가 틱마다 이 행의 Close/High/Low/Volume을
    갱신한다. 아직 하나도 없으면 None. '''
    latest = LatestPrices(stockCode, limit=1)
    return latest[0] if latest else None

def DailyChangePct(stockCode):
    ''' 오늘의 시가(Open) 대비, 지금까지 생성된 마지막 틱 가격(Close)의 등락률(%, 소수점 둘째자리).
    하루 안에서 10초마다 쌓이는 실시간 틱 기준이라, 어제 종가와는 비교하지 않는다. '''
    row = TodayRow(stockCode)
    if not row or not row.Open:
        return 0.0
    return round((row.Close - row.Open) / row.Open * 100, 2)

def PriceHistory(stockCode, days=5):
    ''' 오래된 순으로 최근 days거래일 종가 리스트 (그래프용) '''
    rows = (
        account.session.query(StockPriceEntry)
        .filter(StockPriceEntry.Stock_Code == stockCode)
        .order_by(StockPriceEntry.Trade_Date.desc())
        .limit(days)
        .all()
    )
    return [r.Close for r in reversed(rows)]

if __name__ == '__main__':
    app.run(debug=True, port=5000)