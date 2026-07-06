# external API imports
from sqlalchemy import *
from sqlalchemy.orm import relation, sessionmaker, DeclarativeBase, Mapped, mapped_column

from datetime import datetime
from zoneinfo import ZoneInfo

from flask import Flask, request, jsonify

app = Flask(__name__)

# internal API imports
import account
import friends

# create engine
class Base(DeclarativeBase):
    pass

engine = create_engine('''"dbms://user:pwd@host/dbname''', echo=True)
Base.metadata.create_all(engine)

Session = sessionmaker(autocommit=False, autoflush=False, bind=engine)
session = Session()

# test required
class RankingEntry(Base): 
    __tablename__ = "User_Ranking"

    ID: Mapped[str] = mapped_column(primary_key=True)
    Return_Daily: Mapped[int] = mapped_column(Integer)

    __table_args__ = (
        ForeignKeyConstraint(["ID"], ["User_Info.ID"]),
    )

    # default profile is embedded in website
    def __init__(self, ID="", Return_Daily=0):
        self.ID = ID
        self.Return_Daily = Return_Daily
        
    def __repr__(self):
        return f"Ranking(ID: {self.ID}, Daily Return: {self.Return_Daily})"

Base.metadata.create_all(engine)

def Register(ID):
    user = session.get(UserAccount, ID)

    try:
        session.add(a1)
        session.commit()
    except:
        session.rollback()

# !! WIP !!
def Update():
    '''TODO'''

# !! WIP !!
@app.route('/social', methods=['GET'])
def View():
    if request.is_json:
        data = request.get_json()
    else:
        data = request.form

    userId = data.get()
    user = session.get(UserAccount, userId)

    if not user:
        return jsonify({
            "status": "fail",
            "message": "메인 화면을 불러오는 데 실패했습니다. 다시 로그인해 주세요."
        }), 401

    try:
        stmt = (
            select(AccountStock, StockEntry.Stock_Desc)
            .join(StockEntry, AccountStock.Stock_Name == StockEntry.Stock_Name)
            .where(AccountStock.ID == user.ID)
        )
        user_stocks = session.execute(stmt).all()

        '''
        stmt = (
            select(AccountStock, StockEntry.Stock_Desc)
            .join(StockEntry, AccountStock.Stock_Name == StockEntry.Stock_Name)
            .where(AccountStock.ID == user.ID)
        )
        user_stocks = session.execute(stmt).all()
        '''
        
        # friendRankings
        friendRankingsList = (
            session
            .query(RankingEntry)
            .order_by(RankingEntry.Return_Daily.desc()).limit(10).all()
        )

        # topRankings 
        topRankingsList = (
            session
            .query(RankingEntry)
            .order_by(RankingEntry.Return_Daily.desc()).limit(10).all()
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
            "status": "success",
            "message": "홈 화면을 성공적으로 불러왔습니다."
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
    except:
        return jsonify({
            "status": "fail",
            "message": "홈 화면을 불러오지 못했습니다."
        }), 400

if __name__ == '__main__':
    app.run(debug=True, port=5000)