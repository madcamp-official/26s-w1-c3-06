from sqlalchemy import *
from sqlalchemy.orm import relation, sessionmaker, DeclarativeBase, Mapped, mapped_column

from datetime import datetime
from zoneinfo import ZoneInfo
from decimal import Decimal

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

# !! WIP !!
class UserAccount(Base): 
    __tablename__ = "User_Info"

    ID: Mapped[str] = mapped_column(String(16), primary_key=True)
    PW: Mapped[str] = mapped_column(String(20))
    LastConnect: Mapped[datetime] = mapped_column(Datetime(timezone=True), server_default=func.now())
    Balance: Mapped[int] = mapped_column(Integer)
    Return: Mapped[int] = mapped_column(Integer)
    LastBailout: Mapped[datetime] = mapped_column(Datetime(timezone=True), server_default=func.now())
    Nickname: Mapped[str] = mapped_column(String(12),unique=True)
    Profile: Mapped[bytes] = mapped_column(LargeBinary)

    # default profile is embedded in website
    def __init__(self, ID=None, PW=None):
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

# !! WIP !!
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
        return f"S"

Base.metadata.create_all(engine)

# Create an account and stage onto DB
# !! WIP !!
def Create(ID, PW):
    a1 = UserAccount(ID, PW)
    try:
        session.add(a1)
        session.commit()
    except:
        session.rollback()

# !! WIP !!
def Authenticate(ID, PW):
    user = session.get(UserAccount, ID)

    if user and user.PW == PW:
        try:
            user.LastConnect = datetime.now(ZoneInfo("Asia/Tokyo"))

        except:

# !! WIP !!
def View(ID):
    user = session.get(UserAccount, ID)

    if user:
        try:

        except:

# Test required
def Edit(ID, new_PW, new_Nickname, new_Profile):
    user = session.get(UserAccount, ID)

    if user:
        try: 
            user.PW = new_PW
            user.Nickname = new_Nickname
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


