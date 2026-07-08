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

# Database tables will be created when the Flask app starts
# Base.metadata.create_all(engine)

# ----------------------------------------------------------------------
# Core APIs 
# ----------------------------------------------------------------------

# !! WIP !!
# def PriceUpToDate():
#     pass

@app.route('/stock-list', methods=['GET'])
def View_List():
    '''TODO'''
    pass

@app.route('/stock-detail', methods=['GET'])
def View_Entry():
    '''TODO'''
    pass

if __name__ == '__main__':
    app.run(debug=True, port=5000)