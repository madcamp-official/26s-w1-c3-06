# external API imports
import os

from sqlalchemy import *
from sqlalchemy.orm import relationship, sessionmaker, DeclarativeBase, Mapped, mapped_column

import random
from math import floor
from datetime import datetime, time
from zoneinfo import ZoneInfo
from decimal import Decimal

from flask import Flask, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)


# 로컬에서 프론트(file:// 또는 다른 포트)와 붙여서 테스트할 수 있도록 CORS 허용.
# 이게 없으면 curl로는 정상 응답이 와도, 브라우저 fetch()는 응답을 막아버려서
# JS 쪽에서는 "서버에 연결할 수 없다"처럼 보이는 네트워크 에러로 나타난다.
@app.after_request
def add_cors_headers(response):
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, PATCH, OPTIONS"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type"
    return response


# create engine
# ranking.py/friends.py가 User_Info를 참조하는 FK가 있는 모델을 이 Base 위에 정의하므로(같은 metadata를
# 공유해야 FK 문자열 "User_Info.ID"가 풀린다), 내부 모듈을 import하기 전에 Base부터 정의해야 한다.
# (stock -> news -> friends 처럼 다른 모듈을 거쳐 friends.py가 먼저 로딩될 수 있어서, Base 정의 위치가
# import 블록보다 뒤에 있으면 순환 import 도중 account.Base가 아직 없어 ImportError가 난다.)
class Base(DeclarativeBase):
    pass

# internal API imports
import stock
import order
import news
import quiz
import ranking
import friends

DATABASE_URL = os.environ.get(
    "DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/mockinvest"
)

engine = create_engine(DATABASE_URL, echo=True)
Session = sessionmaker(autocommit=False, autoflush=False, bind=engine)
session = Session()

# README 기획안: 계좌 생성 직후 100만원 시드 자산 지급
SEED_BALANCE = 1_000_000

# test required
class UserAccount(Base):
    __tablename__ = "User_Info"

    ID: Mapped[str] = mapped_column(String(16), primary_key=True)
    PW: Mapped[str] = mapped_column(String(255))
    Reg_Date: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    Balance: Mapped[int] = mapped_column(Integer)
    Return: Mapped[int] = mapped_column(Integer)
    LastBailout: Mapped[bool] = mapped_column(Boolean)
    Nickname: Mapped[str] = mapped_column(String(12),unique=True,nullable=True)
    Profile: Mapped[bytes] = mapped_column(LargeBinary,nullable=True)
        
    def __repr__(self):
        return f"User(ID: {self.ID}, PW: {self.PW}, Balance: {self.Balance})"

# test required
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

    def __init__(self, Stock_Name="", ID="", Own_Quantity=0, Own_Avg=Decimal("0")):
        self.Stock_Name = Stock_Name
        self.ID = ID
        self.Own_Quantity = Own_Quantity
        self.Own_PriceChange = 0
        self.Own_Avg = Own_Avg

    def __repr__(self):
        return f"StockOwned(Name: {self.Stock_Name}, Owner ID: {self.ID}, Quantity: {self.Own_Quantity}, Avg: {self.Own_Avg})"

# ----------------------------------------------------------------------
# Helper Functions
# ----------------------------------------------------------------------
def Midnight(dt):
    return datetime.combine(dt.date(), time.min)

# ----------------------------------------------------------------------
# Core APIs 
# ----------------------------------------------------------------------

@app.route('/auth/check-id', methods=['GET'])
def id_exists():
    if request.is_json:
        data = request.get_json()
    else:
        data = request.form
        
    userId = request.args.get('id')

    try:
        if session.get(UserAccount, userId) is not None:
            return jsonify({
                "status": "success",
                "available": False,
                "message": "아이디가 중복됩니다."
            }), 200
        else:
            return jsonify({
                "status": "success",
                "available": True,
                "message": "사용할 수 있는 아이디입니다."
            }), 200
    except:
        return jsonify({
            "status": "fail",
            "message": "중복 검사에 실패했습니다."
        }), 400

@app.route('/auth/check-nickname', methods=['GET'])
def nickname_exists():
    if request.is_json:
        data = request.get_json()
    else:
        data = request.form

    nickname = request.args.get('nickname')

    try:
        if session.query(UserAccount).filter_by(Nickname=nickname).first() is not None:
            return jsonify({
                "status": "success",
                "available": False,
                "message": "닉네임이 중복됩니다."
            }), 200
        else:
            return jsonify({
                "status": "success",
                "available": True,
                "message": "사용할 수 있는 닉네임입니다."
            }), 200
    except:
        return jsonify({
            "status": "fail",
            "message": "중복 검사에 실패했습니다."
        }), 400

# Create an account and stage onto DB / Redundancy Check (wip)
# !! test required !!
@app.route('/auth/signup', methods=['POST'])
def Create():
    if request.is_json:
        data = request.get_json()
    else:
        data = request.form
    
    nickname = data.get('nickname')
    userId = data.get('id')
    password = data.get('pw')

    if not nickname or not userId or not password:
        return jsonify({
            "status": "fail",
            "message": "유효하지 않은 닉네임, ID 또는 비밀번호. 계정 생성에 실패하였습니다."
        }), 400

    if session.get(UserAccount, userId) is not None or session.query(UserAccount).filter_by(Nickname=nickname).first() is not None:
        return jsonify({
            "status": "fail",
            "message": "아이디 또는 닉네임이 중복됩니다."
        }), 400

    # default profile is embedded in website

    user = UserAccount(
        ID=userId,
        PW=generate_password_hash(password),
        Reg_Date=datetime.now().astimezone(),
        Balance=SEED_BALANCE,
        Return=0,
        LastBailout=False,
        Nickname=nickname,
        Profile=None,
    )

    try:
        session.add(user)
        session.commit()

        return jsonify({
            "status": "success",
            "message": "계정이 생성되었습니다.",
            "id": user.ID,
            "nickname": user.Nickname
        }), 201
    except:
        session.rollback()
        return jsonify({
            "status": "fail",
            "message": "계정 생성에 실패했습니다."
        }), 400

# Receive login request and authenticate
# test required
@app.route('/auth/login', methods=['POST'])
def Authenticate():
    if request.is_json:
        data = request.get_json()
    else:
        data = request.form

    userId = data.get('id')
    password = data.get('pw')

    if not userId or not password:
        return jsonify({
            "status": "fail",
            "message": "사용자 아이디와 비밀번호를 모두 입력해 주세요."
        }), 400

    user = session.get(UserAccount, userId)

    if user and check_password_hash(user.PW, password):
        return jsonify({
            "status": "success",
            "message": "로그인이 완료되었습니다.",
            "id": user.ID
        }), 200
    else:
        return jsonify({
            "status": "fail",
            "message": "아이디 또는 비밀번호가 일치하지 않습니다."
        }), 401

# Show main page and feature (almost) everything
# test required
@app.route('/account', methods=['GET'])
def View():
    if request.is_json:
        data = request.get_json()
    else:
        data = request.form

    userId = request.args.get('id')
    user = session.get(UserAccount, userId)

    if not user:
        return jsonify({
            "status": "fail",
            "message": "메인 화면을 불러오는 데 실패했습니다. 다시 로그인해 주세요."
        }), 401

    try:
        stmt = (
            select(AccountStock, stock.StockEntry.Stock_Desc)
            .join(stock.StockEntry, AccountStock.Stock_Name == stock.StockEntry.Stock_Name)
            .where(AccountStock.ID == user.ID)
        )
        user_stocks = session.execute(stmt).all()
        
        stock_sum = 0
        mockHoldingsList = []

        for holding, desc in user_stocks:
            value = holding.Own_Quantity * holding.Own_Avg
            # mockAccount
            stock_sum += value

            # mockHoldings
            mockHolding = {
                "name": holding.Stock_Name,
                "desc": desc,
                "value": int(value),
                "returnPct": (100 * holding.Own_PriceChange / value).quantize(Decimal('0.1'))
            }
            mockHoldingsList.append(mockHolding)

        # mockNews
        recent_news = (
            session
            .query(news.NewsEntry)
            .order_by(news.NewsEntry.News_Date.desc()).limit(5).all()
        )

        mockNewsList = []

        for article in recent_news:
            mockNewsList.append({
                "title": article.News_Title,
                "source": article.Publisher,
                "link": article.News_Body,
                "date": article.News_Date.strftime("%Y-%m-%d")
            })
        
        return jsonify({
            "status": "success",
            "message": "홈 화면을 성공적으로 불러왔습니다.",
            "mockAccount": {
                "nickname": user.Nickname,
                "virtualDay": (Midnight(datetime.now().astimezone()) - Midnight(user.Reg_Date)).days + 1,
                "totalAsset": user.Balance,
                "profitLoss": user.Return,
                "cashBalance": max([0, int(user.Balance - stock_sum)]),
                "stockCount": len(user_stocks),
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
        
# test required
@app.route('/quiz', methods=['GET'])
def DailyBailout():
    userId = request.args.get('userId')
    user = session.get(UserAccount, userId)

    if not user:
        return jsonify({
            "status": "fail",
            "message": "퀴즈를 불러오는 데 실패했습니다. 다시 로그인해 주세요."
        }), 401

    if user.LastBailout == True:
        return jsonify({
            "status": "success",
            "already_used": True,
            "message": "이미 오늘의 퀴즈를 풀었습니다."
        }), 200

    try:
        # Show a quiz
        quizLength = session.query(quiz.QuizEntry).count()
        quizRanNum = floor(random.random() * quizLength)
        quizToday = quiz.Show(quizRanNum)

        if not quizToday:
            raise ValueError("퀴즈를 찾지 못했습니다.")

        return jsonify({
            "status": "success",
            "message": "오늘의 퀴즈를 불러왔습니다.",
            "quiz_num": quizRanNum,
            "quiz_body": quizToday
        }), 200
    except ValueError as e:
        session.rollback()
        return jsonify({
            "status": "fail",
            "message": "퀴즈 불러오기에 실패했습니다."
        }), 400

# test required
@app.route('/quiz/submit', methods=['POST'])
def SubmitAndReward():
    if request.is_json:
        data = request.get_json()
    else:
        data = request.form

    userId = data.get('userId')
    quiz_num = data.get('quiz_num')
    answerIndex = data.get('answerIndex')

    user = session.get(UserAccount, userId)
    quizToday = session.get(quiz.QuizEntry, quiz_num)

    if not user:
        return jsonify({
            "status": "fail",
            "message": "채점 결과를 불러오는 데 실패했습니다. 다시 로그인해 주세요."
        }), 401
    
    # answer checking
    QuizCorrect = quiz.Check(quiz_num, answerIndex)
    if QuizCorrect is None:
        raise Exception("퀴즈 채점 불가능")

    try:
        already_used = user.LastBailout == True

        if QuizCorrect and not already_used:
            user.Balance += 10000

        if QuizCorrect:
            result = jsonify({
                "status": "success",
                "correct": True,
                "already_used": already_used,
                "balance": user.Balance,
                "message": "퀴즈 정답! 오늘의 보상을 받아가세요."
            }), 200
        else:
            result = jsonify({
                "status": "success",
                "correct": False,
                "already_used": already_used,
                "message": "퀴즈를 틀렸습니다. 내일 다시 기회를 노리세요."
            }), 200

        user.LastBailout = True
        session.commit()
        return result
    except Exception:
        session.rollback()
        return jsonify({
            "status": "fail",
            "message": "퀴즈 채점에 실패했습니다."
        }), 400

# test required
@app.route('/settings', methods=['PATCH'])
def Update():
    if request.is_json:
        data = request.get_json()
    else:
        data = request.form

    userId = data.get('userId')
    user = session.get(UserAccount, userId)

    if not user:
        return jsonify({
            "status": "fail",
            "message": "사용자를 찾지 못했습니다. 다시 로그인해 주세요."
        }), 401

    password = data.get('password')
    nickname = data.get('nickname')
    profile = data.get('profile')

    if not nickname:
        return jsonify({
            "status": "fail",
            "message": "유효하지 않은 닉네임입니다. 계정 정보를 수정하지 못했습니다."
        }), 400

    try:
        if password:
            user.PW = generate_password_hash(password)
        user.Nickname = nickname
        if profile is not None:
            # Profile 컬럼은 bytea라 base64 문자열(data:image/...;base64,...)을 바로 넣을 수 없다.
            user.Profile = profile.encode("utf-8") if isinstance(profile, str) else profile
        session.commit()

        return jsonify({
            "status": "success",
            "message": "계정 정보가 수정되었습니다."
        }), 200
    except:
        session.rollback()
        return jsonify({
            "status": "fail",
            "message": "계정 정보 수정에 실패했습니다."
        }), 400

# test required
@app.route('/settings', methods=['POST'])
def Delete():
    if request.is_json:
        data = request.get_json()
    else:
        data = request.form

    userId = data.get('userId')
    user = session.get(UserAccount, userId)

    if not user:
        return jsonify({
            "status": "fail",
            "message": "사용자를 찾지 못했습니다. 다시 로그인해 주세요."
        }), 401
    
    try:
        # User_Info를 FK로 참조하는 랭킹/친구 관련 행부터 지워야 FK 제약 위반 없이 계정을 지울 수 있다.
        session.execute(delete(ranking.DailySnapshot).where(ranking.DailySnapshot.ID == userId))
        session.execute(delete(ranking.RankingEntry).where(ranking.RankingEntry.ID == userId))
        session.execute(delete(friends.FriendEntry).where(
            or_(friends.FriendEntry.FromID == userId, friends.FriendEntry.ToID == userId)
        ))
        session.execute(delete(UserAccount).where(UserAccount.ID == userId))
        session.commit()

        return jsonify({
            "status": "success",
            "message": "계정이 삭제되었습니다."
        }), 200
    except:
        session.rollback()

        return jsonify({
            "status": "fail",
            "message": "계정 삭제에 실패했습니다."
        }), 400

# test required
@app.route('/social/ranking', methods=['GET'])
def SocialRanking():
    userId = request.args.get('userId')
    user = session.get(UserAccount, userId)

    if not user:
        return jsonify({
            "status": "fail",
            "message": "랭킹을 불러오는 데 실패했습니다. 다시 로그인해 주세요."
        }), 401

    try:
        allUsers = session.query(UserAccount).all()

        entries = []
        for u in allUsers:
            wonDelta = ranking.EnsureTodaySnapshotAndReturn(u)
            pct = ranking.ReturnPct(u, wonDelta)
            entries.append({"user": u, "pct": pct})

        entries.sort(key=lambda e: e["pct"], reverse=True)

        def toRankList(entryList):
            return [
                {
                    "rank": i + 1,
                    "name": e["user"].Nickname,
                    "pct": e["pct"],
                    "isMe": e["user"].ID == userId
                }
                for i, e in enumerate(entryList[:10])
            ]

        globalRanking = toRankList(entries)

        friendIds = set(friends.GetFriendIds(userId))
        friendIds.add(userId)
        friendRanking = toRankList([e for e in entries if e["user"].ID in friendIds])

        return jsonify({
            "status": "success",
            "message": "랭킹을 성공적으로 불러왔습니다.",
            "globalRanking": globalRanking,
            "friendRanking": friendRanking
        }), 200
    except:
        return jsonify({
            "status": "fail",
            "message": "랭킹을 불러오지 못했습니다."
        }), 400

# test required
@app.route('/social/request-friends', methods=['POST'])
def RequestFriends():
    if request.is_json:
        data = request.get_json()
    else:
        data = request.form

    fromId = data.get('fromId')
    toId = data.get('toId')

    entry, message, _ = friends.RequestFriend(fromId, toId)
    if not entry:
        return jsonify({"status": "fail", "message": message}), 400

    return jsonify({
        "status": "success",
        "message": message,
        "fromId": fromId,
        "toId": toId
    }), 200

# test required
@app.route('/social/accept-friends', methods=['POST'])
def AcceptFriends():
    if request.is_json:
        data = request.get_json()
    else:
        data = request.form

    fromId = data.get('fromId')
    toId = data.get('toId')

    ok, message = friends.AcceptFriend(fromId, toId)
    if not ok:
        return jsonify({"status": "fail", "message": message}), 400

    return jsonify({"status": "success", "message": message}), 200

# test required
@app.route('/social', methods=['GET'])
def SocialView():
    userId = request.args.get('userId')
    user = session.get(UserAccount, userId)

    if not user:
        return jsonify({
            "status": "fail",
            "message": "친구 목록을 불러오는 데 실패했습니다. 다시 로그인해 주세요."
        }), 401

    try:
        friendIds = friends.GetFriendIds(userId)
        friendUsers = (
            session.query(UserAccount).filter(UserAccount.ID.in_(friendIds)).all()
            if friendIds else []
        )
        friendList = [{"id": u.ID, "name": u.Nickname} for u in friendUsers]

        pending = friends.GetPendingRequest(userId)
        friendRequest = None
        if pending:
            fromUser = session.get(UserAccount, pending.FromID)
            friendRequest = {
                "fromId": pending.FromID,
                "fromName": fromUser.Nickname if fromUser else pending.FromID
            }

        return jsonify({
            "status": "success",
            "message": "친구 정보를 성공적으로 불러왔습니다.",
            "friendList": friendList,
            "friendRequest": friendRequest
        }), 200
    except:
        return jsonify({
            "status": "fail",
            "message": "친구 정보를 불러오지 못했습니다."
        }), 400

# test required
@app.route('/social/delete-friends', methods=['POST'])
def DeleteFriends():
    if request.is_json:
        data = request.get_json()
    else:
        data = request.form

    fromId = data.get('fromId')
    toId = data.get('toId')

    deleted = friends.DeleteFriend(fromId, toId)
    if not deleted:
        return jsonify({"status": "fail", "message": "삭제할 관계를 찾지 못했습니다."}), 400

    return jsonify({"status": "success", "message": "친구 관계가 삭제되었습니다."}), 200

if __name__ == '__main__':
    app.run(debug=True, threaded=True, port=5000)