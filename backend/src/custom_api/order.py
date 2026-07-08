# external API imports
import os

from sqlalchemy import *
from sqlalchemy.orm import relationship, sessionmaker, DeclarativeBase, Mapped, mapped_column

from datetime import datetime
from zoneinfo import ZoneInfo
from enum import Enum
from decimal import Decimal

from flask import Flask, request, jsonify

app = Flask(__name__)

# internal API imports
import account
import stock
import notify

# define custom types
class ord_pos(Enum):
    BTO = "BTO"
    STC = "STC"

class ord_res(Enum):
    SUCCESS = "SUCCESS"
    FAIL = "FAIL"
    CANCELLED = "CANCELLED"
    PENDING = "PENDING"

from account import Base

DATABASE_URL = os.environ.get(
    "DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/mockinvest"
)

engine = create_engine(DATABASE_URL, echo=True)
Session = sessionmaker(autocommit=False, autoflush=False, bind=engine)
session = Session()

# !! WIP !!
class OrderEntry(Base):
    __tablename__ = "Stock_Order"

    Order_ID: Mapped[int] = mapped_column(Integer, primary_key=True)
    Stock_Code: Mapped[int]
    ID: Mapped[str]
    Order_Quantity: Mapped[int] = mapped_column(Integer)
    Order_Position: Mapped[ord_pos] = mapped_column()
    Order_Result: Mapped[ord_res] = mapped_column()
    Order_Date: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    Order_Price: Mapped[int] = mapped_column(Integer, nullable=True)

    # Stock_Code/ID의 실제 FK 제약은 db/schema.sql에 이미 있다. 이 프로젝트는 모듈마다 별도의
    # DeclarativeBase를 쓰고 있어서(account.py/stock.py/order.py 각자 다른 Base) 여기서
    # ForeignKeyConstraint로 다른 모듈 Base의 테이블을 문자열 참조하면 mapper 설정 시점에
    # NoReferencedTableError가 난다 (notify.py의 링크 테이블들과 같은 이유). 그래서 여기서는
    # 순수 컬럼으로만 매핑한다.

    # default profile is embedded in website
    def __init__(self, Order_ID=0, Stock_Code=0, Buyer_ID="", Order_Quantity=0, Order_Position=None, Order_Result=None, Order_Date=None, Order_Price=None):
        self.Order_ID = Order_ID
        self.Stock_Code = Stock_Code
        self.ID = Buyer_ID
        self.Order_Quantity = Order_Quantity
        self.Order_Position = Order_Position
        self.Order_Result = Order_Result
        self.Order_Date = Order_Date
        self.Order_Price = Order_Price

    def __repr__(self):
        return f"Order(Code: {self.Stock_Code}, Quantity: {self.Order_Quantity}, Position: {self.Order_Position}, Date: {self.Order_Date}, Result: {self.Order_Result})"

# ----------------------------------------------------------------------
# Core APIs
# ----------------------------------------------------------------------
# 실제 HTTP 라우트는 account.py의 account.app에 등록한다 (이 모듈의 app은 main.py에서 실행되지
# 않는 인스턴스라 여기 등록해봐야 호출되지 않는다). 이 파일은 순수 주문 체결 로직만 둔다.

def NextOrderId():
    return (account.session.query(func.coalesce(func.max(OrderEntry.Order_ID), 0)).scalar() or 0) + 1

def CashBalance(user):
    ''' 총자산(Balance)에서 보유 주식의 취득원가 합계를 뺀 실제 현금 보유량.
    매수 가능 수량은 이 값으로 bound가 결정된다. '''
    stockCostSum = account.session.query(
        func.coalesce(func.sum(account.AccountStock.Own_Quantity * account.AccountStock.Own_Avg), 0)
    ).filter(account.AccountStock.ID == user.ID).scalar()
    return max(0, int(user.Balance - stockCostSum))

def ExecuteOrder(userId, stockCode, quantity, position):
    ''' 매수(BTO)/매도(STC) 주문을 체결한다.
    반환: (success: bool, message: str, data: dict|None)

    매수는 "현재가 * 수량 <= 보유 현금(CashBalance)"일 때만 체결된다 (거래량이 현금 보유량으로
    bound됨). 매도는 보유 수량을 넘을 수 없다. 체결 성공/실패 모두 Stock_Order에 기록한다. '''
    user = account.session.get(account.UserAccount, userId)
    if not user:
        return False, "사용자를 찾지 못했습니다. 다시 로그인해 주세요.", None

    stockEntry = account.session.get(stock.StockEntry, stockCode)
    if not stockEntry:
        return False, "종목을 찾지 못했습니다.", None

    if not isinstance(quantity, int) or quantity <= 0:
        return False, "수량은 1 이상이어야 합니다.", None

    if position not in ("BTO", "STC"):
        return False, "잘못된 주문 종류입니다.", None

    price = stock.CurrentPrice(stockCode)
    if price is None:
        return False, "현재가를 불러오지 못했습니다.", None

    holding = account.session.get(account.AccountStock, (stockCode, userId))
    orderDate = datetime.now().astimezone()

    def logOrder(result):
        entry = OrderEntry(
            Order_ID=NextOrderId(),
            Stock_Code=stockCode,
            Buyer_ID=userId,
            Order_Quantity=quantity,
            Order_Position=ord_pos[position],
            Order_Result=result,
            Order_Date=orderDate,
            Order_Price=price,
        )
        account.session.add(entry)
        account.session.flush()  # Notification_Order가 참조할 Stock_Order 행을 먼저 실제로 insert해둔다
        return entry

    if position == "BTO":
        cash = CashBalance(user)
        cost = price * quantity

        if cost > cash:
            logOrder(ord_res.FAIL)
            account.session.commit()
            return False, f"현금이 부족합니다. (보유 현금 {cash:,}원, 필요 금액 {cost:,}원)", None

        if holding:
            totalCost = holding.Own_Quantity * holding.Own_Avg + Decimal(cost)
            holding.Own_Quantity += quantity
            holding.Own_Avg = totalCost / holding.Own_Quantity
        else:
            holding = account.AccountStock(
                Stock_Code=stockCode, ID=userId, Own_Quantity=quantity, Own_Avg=Decimal(price)
            )
            account.session.add(holding)

        orderEntry = logOrder(ord_res.SUCCESS)
        notify.NotifyOrderFilled(orderEntry, stockEntry.Stock_Name, db_session=account.session)
        account.session.commit()
        return True, f"{stockEntry.Stock_Name} {quantity}주 매수 완료", {
            "balance": user.Balance, "cashBalance": CashBalance(user)
        }

    # position == "STC"
    if not holding or holding.Own_Quantity < quantity:
        logOrder(ord_res.FAIL)
        account.session.commit()
        return False, "보유 수량보다 많은 수량을 매도할 수 없습니다.", None

    proceeds = price * quantity
    costBasisRemoved = holding.Own_Avg * quantity
    realizedPnL = int(round(proceeds - costBasisRemoved))

    holding.Own_Quantity -= quantity
    if holding.Own_Quantity == 0:
        account.session.delete(holding)

    user.Balance += realizedPnL
    user.Return += realizedPnL

    orderEntry = logOrder(ord_res.SUCCESS)
    notify.NotifyOrderFilled(orderEntry, stockEntry.Stock_Name, db_session=account.session)
    account.session.commit()
    return True, f"{stockEntry.Stock_Name} {quantity}주 매도 완료 (실현손익 {realizedPnL:+,}원)", {
        "balance": user.Balance, "cashBalance": CashBalance(user)
    }

if __name__ == '__main__':
    app.run(debug=True, port=5000)
