# external API imports
import os

from sqlalchemy import *
from sqlalchemy.orm import relationship, sessionmaker, DeclarativeBase, Mapped, mapped_column

from datetime import datetime
from zoneinfo import ZoneInfo
from enum import Enum

from flask import Flask, request, jsonify

app = Flask(__name__)

# internal API imports
import account
import stock

# define custom types
class ord_pos(Enum):
    BTO = "BTO"
    STC = "STC"

class ord_res(Enum):
    SUCCESS = "SUCCESS"
    FAIL = "FAIL"
    CANCELLED = "CANCELLED"
    PENDING = "PENDING"

# create engine
class Base(DeclarativeBase):
    pass

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
class OrderEntry(Base):
    __tablename__ = "Stock_Order"

    Order_ID: Mapped[int] = mapped_column(Integer, primary_key=True)
    Stock_Code: Mapped[int]
    ID: Mapped[str]
    Order_Quantity: Mapped[int] = mapped_column(Integer)
    Order_Position: Mapped[ord_pos] = mapped_column()
    Order_Result: Mapped[ord_res] = mapped_column()
    Order_Date: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (
        ForeignKeyConstraint(["Stock_Code"], ["Stock_List.Stock_Code"]),
        ForeignKeyConstraint(["ID"], ["User_Info.ID"]),
    )

    # default profile is embedded in website
    def __init__(self, Order_ID, Stock_Code, Buyer_ID="", Order_Quantity=0, Order_Position, Order_Result, Order_Date):
        self.Order_ID = Order_ID
        self.Stock_Code = Stock_Code
        self.ID = Buyer_ID
        self.Order_Quantity = Order_Quantity 
        self.Order_Position = Order_Position
        self.Order_Result = Order_Result
        self.Order_Date = Order_Date

    def __repr__(self):
        return f"Order(Code: {self.Stock_Code}, Quantity: {self.Order_Quantity}, Position: {self.Order_Position}, Date: {self.Order_Date}, Result: {self.Order_Result})"

# ----------------------------------------------------------------------
# Core APIs 
# ----------------------------------------------------------------------

@app.route('/stock-detail', methods=['POST'])
def Create():
    if request.is_json:
        data = request.get_json()
    else:
        data = request.form

    userId = request.args.get('id')
    user = session.get(account.UserAccount, userId)

    stock_code = request.args.get('stock_code')

    tradeType = data.get('tradeType')
    quantity = data.get('quantity')

    if not user:
        return jsonify({
            "status": "fail",
            "message": "주문을 요청하는 데 실패했습니다. 다시 로그인해 주세요."
        }), 401

    try:
        cashBalance = 0 '''현금보유량, account의 helper 함수로 가져옴'''
        orderId = session.query(func.max(OrderEntry.Order_ID)).scalar() + 1 if session.query(func.max(OrderEntry.Order_ID)).scalar() else 1

        
        new_order = OrderEntry(
            Order_ID = orderId,
            Stock_Code = stock_code,
            ID = userId,
            Order_Quantity = quantity,
            Order_Position = ord_pos(tradeType),
            Order_Result = ord_res,
            Order_Date = Order_Date
        )
        session.add(new_order)
        session.commit()

        return jsonify({
            "status": "success",
            "message": "주식을 정상적으로 주문했습니다.",
            "order": new_order
        }), 200 
    except Exception as : 

    except:
        return jsonify({
            "status": "fail",
            "message": "주문에 실패했습니다."
        }), 400

if __name__ == '__main__':
    app.run(debug=True, port=5000)