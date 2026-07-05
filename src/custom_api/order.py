from sqlalchemy import *
from sqlalchemy.orm import relation, sessionmaker, DeclarativeBase, Mapped, mapped_column

from datetime import datetime
from zoneinfo import ZoneInfo
from enum import Enum

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

engine = create_engine('''"dbms://user:pwd@host/dbname''', echo=True)

Session = sessionmaker(autocommit=False, autoflush=False, bind=engine)
session = Session()

# !! WIP !!
class OrderEntry(Base):
    __tablename__ = "Stock_Order"

    Order_ID: Mapped[int] = mapped_column(Integer, primary_key=True)
    Stock_Name: Mapped[str]
    ID: Mapped[str]
    Order_Quantity: Mapped[int] = mapped_column(Integer)
    Order_Position: Mapped[ord_pos] = mapped_column()
    Order_Result: Mapped[ord_res] = mapped_column()
    Order_Date: Mapped[datetime] = mapped_column(Datetime(timezone=True), server_default=func.now())

    __table_args__ = (
        ForeignKeyConstraint(["Stock_Name"], ["Stock_List.Stock_Name"]),
        ForeignKeyConstraint(["ID"], ["User_Info.ID"]),
    )

    # default profile is embedded in website
    def __init__(self, Order_ID=0, Stock_Name="", Buyer_ID="", Order_Quantity=0, Order_Position=None, Order_Result=None, Order_Date=None):
        self.Order_ID = Order_ID
        self.Stock_Name = Stock_Name
        self.ID = Buyer_ID
        self.Order_Quantity = Order_Quantity 
        self.Order_Position = Order_Position
        self.Order_Result = Order_Result
        self.Order_Date = Order_Date

    def __repr__(self):
        return f"Order(Name: {self.Stock_Name})"





Base.metadata.create_all(engine)

def Create():
    '''TODO'''

def Edit():
    '''TODO'''

def Destroy(del_order_id):
    stmt = delete(OrderEntry).where(OrderEntry.Order_ID == del_order_id)

    try: 
        session.execute(stmt)
        session.commit()
    except:
        session.rollback()