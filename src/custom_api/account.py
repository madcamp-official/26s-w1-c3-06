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
import friends

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
    LastConnect: Mapped[datetime] = mapped_column(Datetime(timezone=True), server_default=func.now())
    Balance: Mapped[int] = mapped_column(Integer)
    Return: Mapped[int] = mapped_column(Integer)
    LastBailout: Mapped[datetime] = mapped_column(Datetime(timezone=True), server_default=func.now())
    Nickname: Mapped[Optional[str]] = mapped_column(String(12),unique=True)
    Profile: Mapped[Optional[bytes]] = mapped_column(LargeBinary)

    # default profile is embedded in website
    def __init__(self, ID="", PW=""):
        self.ID = ID
        self.PW = PW
        self.LastConnect = datetime.now(ZoneInfo("Asia/Tokyo"))
        self.Balance = 0
        self.Return = 0
        self.LastBailout = datetime.now(ZoneInfo("Asia/Tokyo"))
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
def Create(ID, PW):
    a1 = UserAccount(ID, generate_password_hash(PW))
    try:
        session.add(a1)
        session.commit()
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

    ID = data.get()
    PW = data.get()

    if not ID or not PW:
        return jsonify({
                "status": "fail",
                "message": "사용자 아이디와 비밀번호를 모두 입력해 주세요."
        }), 400
    user = session.get(UserAccount, ID)

    if user and check_password_hash(user.PW, PW):
        return jsonify({
            "status": "success",
            "message": "로그인이 완료되었습니다."
            "user_info": {
                "username": user.ID
            }
        }), 200
    else:
        return jsonify({
            "status": "fail",
            "message": "아이디 또는 비밀번호가 일치하지 않습니다."
        }), 401

# Show main page and feature (almost) everything
# !! WIP !!
@app.route('/home', methods=['GET'])
def View(ID):
    if request.is_json:
        data = request.get_json()
    else:
        data = request.form
    
    ID = data.get()
    PW = data.get()
    
    user = session.get(UserAccount, ID)

    if user:
        try:

        except:

# Test required
def Update(ID, new_PW=None, new_Nickname=None, new_Profile=None):
    user = session.get(UserAccount, ID)

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

# Helper Function: midnight of certain datetime object
def Midnight(dt):
    return datetime.combine(dt.date(), time.min)

# html request Required
def DailyBailout(ID):
    user = session.get(UserAccount, ID)
    tokyo_time = datetime.now(ZoneInfo("Asia/Tokyo"))

    if user and (Midnight(tokyo_time) - Midnight(user.LastBailout)).days > 0:
        try:
            user.Balance += 10000
            user.LastBailout = tokyo_time

            session.commit()
        except:
            session.rollback()

# html request required
def Delete(ID):
    stmt = delete(UserAccount).where(UserAccount.ID == ID)

    try:
        session.execute(stmt)
        session.commit()
    except:
        session.rollback()

if __name__ == '__main__':
    app.run(debug=True, port=5000)