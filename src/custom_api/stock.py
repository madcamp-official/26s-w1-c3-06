# external API imports
from sqlalchemy import *
from sqlalchemy.orm import relation, sessionmaker, DeclarativeBase, Mapped, mapped_column

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

engine = create_engine('''"dbms://user:pwd@host/dbname''', echo=True)
Base.metadata.create_all(engine)

Session = sessionmaker(autocommit=False, autoflush=False, bind=engine)
session = Session()

# !! WIP !!
class StockEntry(Base):
    __tablename__ = "Stock_List"

    Stock_Name: Mapped[str] = mapped_column(String(20), primary_key=True)
    Stock_Logo: Mapped[bytes] = mapped_column(LargeBinary)

    def __init__(self, Stock_Name="", Stock_Logo=None):
        self.Stock_Name = Stock_Name
        self.Stock_Logo = Stock_Logo

    def __repr__(self):
        return f"Stock(Name: {self.Stock_Name})"

# !! WIP !!
class StockPriceEntry(Base):
    __tablename__ = "Stock_DailyPrice"

    Trade_Date: Mapped[datetime.datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), primary_key=True)
    Stock_Name: Mapped[str] = mapped_column(primary_key=True)
    Open: Mapped[int] = mapped_column(Integer)
    High: Mapped[int] = mapped_column(Integer)
    Low: Mapped[int] = mapped_column(Integer)
    Close: Mapped[int] = mapped_column(Integer)
    Volume: Mapped[int] = mapped_column(Integer)

    __table_args__ = (
        ForeignKeyConstraint(["Stock_Name"], ["Stock_List.Stock_Name"]),
    )

    # default profile is embedded in website
    def __init__(self, Trade_Date=None, Stock_Name="", Open=0, High=0, Low=0, Close=0, Volume=0):
        self.Trade_Date = Trade_Date
        self.Stock_Name = Stock_Name
        self.Open = Open
        self.High = High
        self.Low = Low
        self.Close = Close
        self.Volume = Volume

    def __repr__(self):
        return f"StockPrice(Date: {self.Trade_Date}, Name: {self.Stock_Name}, High: {self.High}, Low: {self.Low}, Open: {self.Open}, Close: {self.Close})"

Base.metadata.create_all(engine)

# !! WIP !!
def PriceUpToDate():
    
# !! WIP !!
@app.route('/stock-list', methods=['GET'])
def View_List():
    '''TODO'''

# !! WIP !!
@app.route('/stock-detail', methods=['GET'])
def View_Entry():
    '''TODO'''

if __name__ == '__main__':
    app.run(debug=True, port=5000)

