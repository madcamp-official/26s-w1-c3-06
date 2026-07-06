# external API imports
from sqlalchemy import *
from sqlalchemy.orm import relation, sessionmaker, DeclarativeBase, Mapped, mapped_column

import json
from datetime import datetime
from zoneinfo import ZoneInfo

from flask import Flask, request, jsonify

app = Flask(__name__)

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
    Reporter: Mapped[Optional[str]] = mapped_column(String(10))
    Publisher: Mapped[Optional[str]] = mapped_column(String(10))
    News_Date: Mapped[datetime] = mapped_column(Datetime(timezone=True), server_default=func.now())

    def __init__(self, ID=0, title="", body="", reporter=None, publisher=None, news_date=None):
        self.News_ID = ID
        self.News_Title = title
        self.News_Body = body
        self.Reporter = reporter
        self.Publisher = publisher
        self.News_Date = news_date
        
    def __repr__(self):
        return f"News(ID: {self.News_ID}, Title: {self.News_Title}, Reporter: {self.Reporter})"

# test required
class StockNewsEntry(Base):
    __tablename__ = "News_Related"

    Related_Ord: Mapped[int]: mapped_column(Integer, primary_key=True)
    Stock_Name: Mapped[str]
    News_ID: Mapped[int]

    __table_args__ = (
        ForeignKeyConstraint(["Stock_Name"], ["Stock_List.Stock_Name"]),
        ForeignKeyConstraint(["News_ID"], ["News_List.News_ID"]),
    )

    # default profile is embedded in website
    def __init__(self, Related_Ord=0, Stock_Name="", News_ID=0):
        self.Related_Ord = Related_Ord
        self.Stock_Name = Stock_Name
        self.News_ID = News_ID

    def __repr__(self):
        return f"Stock News(News Order: {self.Related_Ord}, Stock Name: {self.Stock_Name}, News ID: {self.News_ID})"

Base.metadata.create_all(engine)

if __name__ == '__main__':
    app.run(debug=True, port=5000)