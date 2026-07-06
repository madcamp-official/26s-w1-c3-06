from sqlalchemy import *
from sqlalchemy.orm import relation, sessionmaker, DeclarativeBase, Mapped, mapped_column

# external API imports
from datetime import datetime
from zoneinfo import ZoneInfo
from decimal import Decimal

from flask import Flask, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)

# internal API imports
import stock
import order
import news
import quiz

# Helper Function: midnight of certain datetime object
def Midnight(dt):
    return datetime.combine(dt.date(), time.min)

# create engine
class Base(DeclarativeBase):
    pass

engine = create_engine('''"dbms://user:pwd@host/dbname''', echo=True)

Session = sessionmaker(autocommit=False, autoflush=False, bind=engine)
session = Session()

# test required
class UserAccount(Base): 
    __tablename__ = "User_Info"

    ID: Mapped[str] = mapped_column(String(16), primary_key=True)
    PW: Mapped[str] = mapped_column(String(255))
    Reg_Date: Mapped[datetime] = mapped_column(Datetime(timezone=True), server_default=func.now())
    Balance: Mapped[int] = mapped_column(Integer)
    Return: Mapped[int] = mapped_column(Integer)
    LastBailout: Mapped[bool] = mapped_column(Boolean)
    Nickname: Mapped[Optional[str]] = mapped_column(String(12),unique=True)
    Profile: Mapped[Optional[bytes]] = mapped_column(LargeBinary)

    # default profile is embedded in website
    def __init__(self, ID="", PW=""):
        self.ID = ID
        self.PW = PW
        self.Reg_Date = datetime.now(ZoneInfo("Asia/Tokyo"))
        self.Balance = 0
        self.Return = 0
        self.LastBailout = False
        self.Nickname = None
        self.Profile = None
        
    def __repr__(self):
        return f"User(ID: {self.ID}, PW: {self.PW}, Balance: {self.Balance})"

# test required
class AccountStock(Base):
    __tablename__ = "Stock_Owned"

    Stock_Name: Mapped[str] = mapped_column(primary_key=True)
    ID: Mapped[str]
    Own_Quantity: Mapped[int] = mapped_column(Integer)
    Own_PriceChange: Mapped[int] = mapped_column(Integer)
    Own_Avg: Mapped[Decimal] = mapped_column(Numeric(12, 4))

    __table_args__ = (
        ForeignKeyConstraint(["Stock_Name"], ["Stock_List.Stock_Name"]),
        ForeignKeyConstraint(["ID"], ["User_Info.ID"]),
    )

    # default profile picture is embedded in website
    def __init__(self, Stock_Name="", ID="", Own_Quantity=0, Own_Avg=Decimal("0")):
        self.Stock_Name = Stock_Name
        self.ID = ID
        self.Own_Quantity = Own_Quantity
        self.Own_PriceChange = 0
        self.Own_Avg = Own_Avg

    def __repr__(self):
        return f"StockOwned(Name: {self.Stock_Name}, Owner ID: {self.ID}, Quantity: {self.Own_Quantity}, Avg: {self.Own_Avg})"

Base.metadata.create_all(engine)

#─────────────────────────────────────────────────────────────────────────────────────────────────────────────#

# Create an account and stage onto DB
# test required
@app.route('/signup', methods=['POST'])
def Create():
    if request.is_json:
        data = request.get_json()
    else:
        data = request.form
    
    nickname = data.get()
    userId = data.get()
    password = data.get()

    if not nickname or not userId or not password:
        return jsonify({
            "status": "fail",
            "message": "유효하지 않은 닉네임, ID 또는 비밀번호. 계정 생성에 실패하였습니다."
        }), 400
    a1 = UserAccount(userId, generate_password_hash(password))

    try:
        session.add(a1)
        session.commit()
        return jsonify({
            "status": "success",
            "message": "계정이 생성되었습니다."
            "userId": user.ID
            "nickname": user.Nickname
        }), 200
    except:
        session.rollback()

# Receive login request and authenticate
# test required
@app.route('/index', methods=['POST'])
def Authenticate():
    if request.is_json:
        data = request.get_json()
    else:
        data = request.form

    userId = data.get()
    password = data.get()

    if not userId or not password:
        return jsonify({
                "status": "fail",
                "message": "사용자 아이디와 비밀번호를 모두 입력해 주세요."
        }), 400
    user = session.get(UserAccount, userID)

    if user and check_password_hash(user.PW, password):
        return jsonify({
            "status": "success",
            "message": "로그인이 완료되었습니다."
            "userId": user.ID
        }), 200
    else:
        return jsonify({
            "status": "fail",
            "message": "아이디 또는 비밀번호가 일치하지 않습니다."
        }), 401

# Show main page and feature (almost) everything
# test required
@app.route('/home', methods=['GET'])
def View():
    if request.is_json:
        data = request.get_json()
    else:
        data = request.form

    userId = data.get()
    user = session.get(UserAccount, userId)

    if user:
        stmt = (
            select(AccountStock, StockEntry.Stock_Desc)
            .join(StockEntry, AccountStock.Stock_Name == StockEntry.Stock_Name)
            .where(AccountStock.ID == user.ID)
        )
        user_stocks = session.execute(stmt).all()
        
        stock_sum = 0
        mockHoldingsList = []

        for stock, desc in user_stocks:
            value = stock.Own_Quantity * stock.Own_Avg
            # mockAccount
            stock_sum += value
            
            # mockHoldings
            mockHolding = {
                "name": stock.Stock_Name,
                "desc": desc,
                "value": int(value),
                "returnPct": (100 * stock.Own_PriceChange / value).quantize(Decimal('0.1'))
            }
            mockHoldingsList.append(mockHolding)   

        # mockNews
        recent_news = (
            session
            .query(StockNewsEntry)
            .order_by(StockNewsEntry.News_Date.desc()).limit(5).all()
        )

        mockNewsList = []

        for news in recent_news:
            mockNews = {
                "title": news.News_Title,
                "source": news.Publisher,
                "link": news.News_Body
            }
            mockNewsList.append(mockNews)
        
        return jsonify({
            "mockAccount": {
                "nickname": user.Nickname
                "virtualDay": (Midnight(tokyo_time) - Midnight(user.Reg_Date)).days + 1
                "totalAsset": user.Balance
                "profitLoss": user.Return
                "cashBalance": max([0, int(user.Balance - stock_sum)])
                "stockCount": len(user_stocks)
                "hasReceivedIncomeToday": user.LastBailout
            },
            "mockHoldings": mockHoldingsList,
            "mockNews": mockNewsList
        }), 200
    else:
        return jsonify({
            "status": "fail",
            "message": "메인 화면을 불러오는 데 실패했습니다. 다시 로그인해 주세요."
        }), 401

# test required
@app.route('/home', methods=['POST'])
def DailyBailout(ID):
    user = session.get(UserAccount, ID)
    tokyo_time = datetime.now(ZoneInfo("Asia/Tokyo"))

    if user and user.LastBailout == False:
        try:
            user.Balance += 10000
            user.LastBailout = True

            session.commit()
        except:
            session.rollback()

# !! WIP !!
@app.route('/settings', methods=['POST'])
def Update():

    ID = data.get()
    user = session.get(UserAccount, ID)

    new_PW = 
    new_Nickname = 
    new_Profile = 

    if user:
        try: 
            if new_Pw is not None:
                user.PW = new_PW
            if new_Nickname is not None:
                user.Nickname = new_Nickname
            if new_Profile is not None:
                user.Profile = new_Profile
            session.commit()
        except:
            session.rollback()

# !! WIP !!
@app.route('/settings', methods=['POST'])
def Delete():
    ID = data.get()
    user = session.get(UserAccount, ID)

    stmt = delete(UserAccount).where(UserAccount.ID == ID)

    try:
        session.execute(stmt)
        session.commit()
    except:
        session.rollback()

if __name__ == '__main__':
    app.run(debug=True, port=5000)