from sqlalchemy import *
from sqlalchemy.orm import relation, sessionmaker, DeclarativeBase, Mapped, mapped_column

from datetime import datetime
from zoneinfo import ZoneInfo

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
    PW = Column(VARCHAR(20))
    LastConnect = Column(TIMESTAMPTZ)
    Balance = Column(INTEGER)
    Return = Column(INTEGER)
    LastBailout = Column(TIMESTAMPTZ)
    Nickname = Column(TEXT)
    Profile = Column(BINARY)

    # default profile is embedded in website
    def __init__(self, ID=None, PW=None):
        self.ID = ID
        self.PW = PW
        self.LastConnect = datetime.now(ZoneInfo("Asia/Tokyo"))
        self.Balance = 0
        self.Return = 0
        self.LastBailout = None
        self.Nickname = None
        self.Profile = None
    def __repr__(self):
        return f"User({self.ID}, {self.Nickname}, {self.Balance})"

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

    user.LastConnect = datetime.now(ZoneInfo("Asia/Tokyo"))

# !! WIP !!
def View(user):
    '''TODO'''

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

# !! WIP !!
def DailyBailout(ID):
    user = session.get(UserAccount, ID)
    tokyo_time = datetime.now(ZoneInfo("Asia/Tokyo"))

    if user and (tokyo_time - user.LastBailout).days > 0:
        try:
            user.Balance += 10000
            user.LastBailout = tokyo_time

            session.commit()
        except:
            session.rollback()

# Test required
def Delete(ID):
    stmt = delete(UserAccount).where(UserAccount.ID == ID)

    try:
        session.execute(stmt)
        session.commit()
    except:
        session.rollback()


