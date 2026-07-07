# external API imports
from sqlalchemy import *
from sqlalchemy.orm import relationship, sessionmaker, DeclarativeBase, Mapped, mapped_column

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

    def __init__(self, ID="", Return_Daily=0):
        self.ID = ID
        self.Return_Daily = Return_Daily
        
    def __repr__(self):
        return f"Ranking(ID: {self.ID}, Daily Return: {self.Return_Daily})"

Base.metadata.create_all(engine)

def Register(ID):
    user = session.get(account.UserAccount, ID)

    try:
        session.add(a1)
        session.commit()
    except:
        session.rollback()

# !! WIP !!
def Update():
    ''' RankingEntry.Return_Daily 일일수익 계산식'''
    '''TODO'''

# test required
@app.route('/social/ranking', methods=['GET'])
def View():
    if request.is_json:
        data = request.get_json()
    else:
        data = request.form

    userId = data.get('userId')
    user = session.get(account.UserAccount, userId)

    if not user:
        return jsonify({
            "status": "fail",
            "message": "랭킹을 불러오는 데 실패했습니다. 다시 로그인해 주세요."
        }), 401

    try:
        # friends list (temporary)
        stmt = (
            select(account.UserAccount, friends.FriendEntry.fromID)
            .join(friends.FriendEntry, account.UserAccount.ID == friends.FriendEntry.toID)
            .where(friends.FriendEntry.fromID == user.ID)
        )
        friendList = session.execute(stmt).all()

        # friendRankings (including me) and topRankings 
        stmt = (
            select(RankingEntry, account.UserAccount)
            .join(account.UserAccount, RankingEntry.ID == account.UserAccount.ID)
        )
        topRankingsList = (
            session.execute(stmt).
            order_by(RankingEntry.Return_Daily.desc()).limit(10).all()
        )
        friendRankingsList = (
            session.execute(stmt).
            filter(account.UserAccount.ID == userId or account.UserAccount.ID in friendList).
            order_by(RankingEntry.Return_Daily.desc()).limit(10).all()
        )

        mockGlobalRanking, mockFriendRanking = [], []
        
        i = 0
        for rank in topRankingsList:
            i += 1
            mockRank = {
                "rank": i,
                "name": rank.Nickname,
                "pct": rank.Return_Daily,
                "isMe": rank.ID == userId
            }
            mockGlobalRanking.append(mockRank)
        
        i = 0
        for rank in friendRankingsList:
            i += 1
            mockRank = {
                "rank": i,
                "name": rank.Nickname,
                "pct": rank.Return_Daily,
                "isMe": rank.ID == userId
            }
            mockFriendRanking.append(mockRank)
        
        return jsonify({
            "status": "success",
            "message": "랭킹을 성공적으로 불러왔습니다.",
            "mockFriendRanking": mockFriendRanking,
            "mockGlobalRanking": mockGlobalRanking
        }), 200
    except:
        return jsonify({
            "status": "fail",
            "message": "랭킹을 불러오지 못했습니다."
        }), 400

if __name__ == '__main__':
    app.run(debug=True, port=5000)