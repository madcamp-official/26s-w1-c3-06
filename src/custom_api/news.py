from sqlalchemy import *
from sqlalchemy.orm import relation, sessionmaker, DeclarativeBase, Mapped, mapped_column

# external API imports
import json
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
Base.metadata.create_all(engine)

Session = sessionmaker(autocommit=False, autoflush=False, bind=engine)
session = Session()

# test required
class NewsEntry(Base): 
    __tablename__ = "News_List"

    News_ID: Mapped[int] = mapped_column(Integer, primary_key=True)
    News_Title: Mapped[str] = mapped_column(Text)
    News_Body: Mapped[str] = mapped_column(Text)
    Reporter: Mapped[str] = mapped_column(String(10))
    Publisher: Mapped[str] = mapped_column(String(10))
    News_Date: Mapped[datetime] = mapped_column(Datetime(timezone=True), server_default=func.now())

    # default profile is embedded in website
    def __init__(self, ID=0, title="", body="", reporter="", publisher="", news_date=None):
        self.News_ID = ID
        self.News_Title = title
        self.News_Body = body
        self.Reporter = reporter
        self.Publisher = publisher
        self.News_Date = news_date
        
    def __repr__(self):
        return f"News(ID: {self.News_ID}, Title: {self.News_Title}, Reporter: {self.Reporter})"

Base.metadata.create_all(engine)