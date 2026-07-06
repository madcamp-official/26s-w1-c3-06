# external API imports

from sqlalchemy import *
from sqlalchemy.orm import relation, sessionmaker, DeclarativeBase, Mapped, mapped_column

from enum import Enum
from datetime import datetime
from zoneinfo import ZoneInfo

from flask import Flask, request, jsonify

app = Flask(__name__)

# internal API imports
import account
import notify

# define custom types
class fnd_sts(Enum):
    REQUESTED = "REQUESTED"
    FRIENDS = "FRIENDS"
    UNRELATED = "UNRELATED"

# create engine
class Base(DeclarativeBase):
    pass

engine = create_engine('''"dbms://user:pwd@host/dbname''', echo=True)
Base.metadata.create_all(engine)

Session = sessionmaker(autocommit=False, autoflush=False, bind=engine)
session = Session()

# ----------------------------------------------------------------------
# Core APIs 
# ----------------------------------------------------------------------

# test required
class FriendEntry(Base):
    __tablename__ = "User_Friends"

    FromID: Mapped[str] = mapped_column(primary_key=True)
    ToID: Mapped[str] = mapped_column(primary_key=True)
    Friend_Date: Mapped[datetime] = mapped_column(Datetime(timezone=True), server_default=func.now())
    Friend_Status: Mapped[fnd_sts] = mapped_column()
    
    __table_args__ = (
        ForeignKeyConstraint(["FromID"], ["User_Info.ID"]),
        ForeignKeyConstraint(["ToID"], ["User_Info.ID"]),
    )

    def __init__(self, FromID="", ToID="", status=fnd_sts.REQUESTED):
        self.FromID = FromID
        self.ToID = ToID
        self.Friend_Date = datetime.now().astimezone()
        self.Friend_Status = status
        
    def __repr__(self):
        return f"Friend(SelfID: {self.FromID}, FriendID: {self.ToID}, Date: {self.Freind_Date} Status: {self.Friend_Status})"

Base.metadata.create_all(engine)

# test required
@app.route('/social', methods=['POST'])
def Request():
    if request.is_json:
        data = request.get_json()
    else:
        data = request.form

    fromId = data.get()
    toId = data.get()
    fromUser = session.get(UserAccount, fromId)
    toUser = session.get(UserAccount, toId)

    if not fromUser:
        return jsonify({
            "status": "fail",
            "message": "사용자를 찾지 못했습니다. 다시 로그인해 주세요."
        }), 401
    
    if not toUser:
        return jsonify({
            "status": "fail",
            "message": "친구 추가를 요청할 사용자를 찾지 못했습니다."
        }), 401
    
    try:
        notify.FriendsNotice(fromId, toId)
        return jsonify({
            "status": "success",
            "message": toUser.Nickname + "님에게 친구 요청을 전송했습니다.",
            "notiTime": datetime.now().astimezone()
            "fromId": fromId,
            "toId": toId
        }), 200
    except:
        return jsonify({
            "status": "fail",
            "message": "친구 요청에 실패했습니다."
        }), 400

# !! WIP !!
@app.route('/social', methods=['POST'])
def Accept():
    '''TODO'''

# !! WIP !!
@app.route('/social', methods=['GET'])
def View():
    '''TODO'''

# test required /// frontend not implemented yet
@app.route('/social', methods=['POST'])
def Delete():
    if request.is_json:
        data = request.get_json()
    else:
        data = request.form

    fromId = data.get()
    toId = data.get()
    fromUser = session.get(UserAccount, fromId)
    toUser = session.get(UserAccount, toId)

    if not fromUser:
        return jsonify({
            "status": "fail",
            "message": "사용자를 찾지 못했습니다. 다시 로그인해 주세요."
        }), 401
    
    try:
        stmt = delete(FriendEntry).where(FriendEntry.ID == toId)

        session.execute(stmt)
        session.commit()

        return jsonify({
            "status": "success",
            "message": "친구가 삭제되었습니다."
        }), 200
    except:
        session.rollback()

        return jsonify({
            "status": "fail",
            "message": "친구 삭제에 실패했습니다."
        }), 400

if __name__ == '__main__':
    app.run(debug=True, port=5000)