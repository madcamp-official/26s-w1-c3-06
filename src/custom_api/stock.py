from sqlalchemy import *
from sqlalchemy.orm import relation, sessionmaker, DeclarativeBase, Mapped, mapped_column

from datetime import datetime
from zoneinfo import ZoneInfo

# internal API imports
import account

# create engine
class Base(DeclarativeBase):
    pass

engine = create_engine('''"dbms://user:pwd@host/dbname''', echo=True)
Base.metadata.create_all(engine)

Session = sessionmaker(autocommit=False, autoflush=False, bind=engine)
session = Session()

# !! WIP !!
class StockEntry(Base): ''' align with post 2.0 syntax'''
    __tablename__ = "Stock_List"

    Stock_Name = Column(VARCHAR(20), primary_key=True)
    Stock_Logo = Column(BINARY)

    # default profile is embedded in website
    def __init__(self, Stock_Name="", Stock_Logo=None):
        self.Stock_Name = Stock_Name
        self.Stock_Logo = Stock_Logo

    def __repr__(self):
        return f"Stock({self.Stock_Name})"

class StockPriceEntry(Base): ''' align with post 2.0 syntax'''
    __tablename__ = "Stock_DailyPrice"

    Stock_Name = Column(VARCHAR(20), primary_key=True)
    Stock_Logo = Column(BINARY)

    # default profile is embedded in website
    def __init__(self, Stock_Name="", Stock_Logo=None):
        self.Stock_Name = Stock_Name
        self.Stock_Logo = Stock_Logo

    def __repr__(self):
        return f"Stock({self.Stock_Name}, {self.Nickname}, {self.Balance})"

def PriceUpToDate():
    

def View_List():
    '''TODO'''

def View_Entry():
    '''TODO'''