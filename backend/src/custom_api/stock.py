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

# create engine
class Base(DeclarativeBase):
    pass

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

# !! WIP !!
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

# Database tables will be created when the Flask app starts
# Base.metadata.create_all(engine)

# ----------------------------------------------------------------------
# Helper Functions
# ----------------------------------------------------------------------
def LatestPriceDate():
    ''' Stock_DailyPrice에 있는 가장 최근 주식 시세 날짜(일자와 시각). 시세가 없으면 None.'''
    latest = session.query(func.max(StockPriceEntry.Trade_Date)).scalar()
    return latest.date() if latest else None

# ----------------------------------------------------------------------
# Core APIs 
# ----------------------------------------------------------------------

# !! WIP !!
def PriceUpToDate():
    pass

# !! WIP - real-time stock price required !!
@app.route('/stock-list', methods=['GET'])
def View_List():
    if request.is_json:
        data = request.get_json()
    else:
        data = request.form
    
    userId = request.args.get('userId')
    user = session.get(account.UserAccount, userId)

    if not user:
        return jsonify({
            "status": "fail",
            "message": "주식 리스트를 불러오는 데 실패했습니다. 다시 로그인해 주세요."
        }), 401

    try:
        latestDate = LatestPriceDate()
        if not latestDate:
            return jsonify({
                "status": "success",
                "message": "시세 정보가 없습니다.",
                "mockStocks": []
            }), 200

        stmt = (
            select(StockPriceEntry, StockEntry)
            .join(StockEntry, StockEntry.Stock_Code == StockPriceEntry.Stock_Code)
            .where(
                func.date(StockPriceEntry.Trade_Date) == latestDate
            )
            .order_by(StockEntry.Stock_Name.asc())
        )
        stocks = session.execute(stmt).scalars().all()

        mockStocksList = [{
            "name": s.Stock_Name,
            "desc": s.Stock_Desc,
            "price": s.Stock_Price, '''블랙숄즈에 의한 실시간 가격'''
            "changePct": (s.Stock_Price - s.Open) / s.Open * 100 if s.Open != 0 else 0 '''실시간 가격이 반영됨'''
        } for s in stocks]

        return jsonify({
            "status": "success",
            "message": "주식 리스트를 성공적으로 불러왔습니다.",
            "mockStocks": mockStocksList
        }), 200
    except:
        return jsonify({
            "status": "fail",
            "message": "주식 리스트를 불러오지 못했습니다."
        }), 400

# !! WIP !!
@app.route('/stock-detail', methods=['GET'])
def View_Entry():
    if request.is_json:
        data = request.get_json()
    else:
        data = request.form

    userId = request.args.get('id')
    user = session.get(account.UserAccount, userId)

    if not user:
        return jsonify({
            "status": "fail",
            "message": "주식 시세를 불러오는 데 실패했습니다. 다시 로그인해 주세요."
        }), 401

    stock_code = request.args.get('stock_code')
    stock = session.get(StockEntry, stock_code)

    try:
        stmt = (
            select(StockPriceEntry, StockEntry)
            .join(StockEntry, StockEntry.Stock_Code == StockPriceEntry.Stock_Code)
            .where(
                func.date(StockPriceEntry.Trade_Date) == latestDate and StockEntry.Stock_Code == stock_code
            )
        )
        targetPriceHistory = session.execute(stmt).scalars().all()

        return jsonify({
            "status": "success",
            "message": "주식 시세를 불러왔습니다.",
            "name": targetPriceHistory[0].Stock_Name,
            "desc": targetPriceHistory[0].Stock_Desc,
            "currentPrice": targetPriceHistory[-1].Stock_Price, '''블랙숄즈에 의한 실시간 가격'''
            "changePct": (
                    (targetPriceHistory[-1].Stock_Price - targetPriceHistory[0].Stock_Price) / 
                    targetPriceHistory[0].Stock_Price * 100
                    if targetPriceHistory[0].Stock_Price != 0 else 0
                ) '''실시간 가격이 반영됨''',
            "priceHistory": [p.Stock_Price for p in targetPriceHistory]
        }), 200
    except:
        return jsonify({
            "status": "fail",
            "message": "주식 시세를 불러오지 못했습니다."
        }), 400


if __name__ == '__main__':
    app.run(debug=True, port=5000)