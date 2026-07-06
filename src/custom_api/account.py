import os

from sqlalchemy import create_engine, String, Integer, Boolean, LargeBinary, TIMESTAMP
from sqlalchemy.orm import sessionmaker, DeclarativeBase, Mapped, mapped_column

from datetime import datetime
from typing import Optional

from werkzeug.security import generate_password_hash, check_password_hash

# 인증 범위만 다룬다 (회원가입/로그인/중복확인). User_Info는 다른 테이블에 대한 FK가 없는
# 기반 테이블이라 이 모듈만으로 독립적으로 동작한다.


class Base(DeclarativeBase):
    pass


# db/schema.sql을 미리 적용해둔 로컬 PostgreSQL을 사용한다.
# 필요하면 DATABASE_URL 환경변수로 접속 정보를 덮어쓸 수 있다.
DATABASE_URL = os.environ.get(
    "DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/mockinvest"
)

engine = create_engine(DATABASE_URL, echo=True)
Session = sessionmaker(autocommit=False, autoflush=False, bind=engine)
session = Session()


class UserAccount(Base):
    __tablename__ = "User_Info"

    ID: Mapped[str] = mapped_column(String(16), primary_key=True)
    PW: Mapped[Optional[str]] = mapped_column(String(255))
    Reg_Date: Mapped[Optional[datetime]] = mapped_column(TIMESTAMP(timezone=True))
    Balance: Mapped[Optional[int]] = mapped_column(Integer)
    Return: Mapped[Optional[int]] = mapped_column(Integer)
    LastBailout: Mapped[Optional[bool]] = mapped_column(Boolean)
    Nickname: Mapped[Optional[str]] = mapped_column(String(12), unique=True)
    Profile: Mapped[Optional[bytes]] = mapped_column(LargeBinary)

    def __repr__(self):
        return f"User(ID={self.ID}, Nickname={self.Nickname}, Balance={self.Balance})"


# README 기획안: 계좌 생성 직후 100만원 시드 자산 지급
SEED_BALANCE = 1_000_000


def id_exists(id_):
    return session.get(UserAccount, id_) is not None


def nickname_exists(nickname):
    return session.query(UserAccount).filter_by(Nickname=nickname).first() is not None


def create(id_, pw, nickname):
    """회원가입. 성공하면 UserAccount, 아이디/닉네임이 이미 있으면 None을 반환한다."""
    if id_exists(id_) or nickname_exists(nickname):
        return None

    user = UserAccount(
        ID=id_,
        PW=generate_password_hash(pw),
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
        return user
    except Exception:
        session.rollback()
        return None


def authenticate(id_, pw):
    """로그인 검증. 성공하면 UserAccount, 아이디가 없거나 비밀번호가 틀리면 None을 반환한다."""
    user = session.get(UserAccount, id_)

    if user and user.PW and check_password_hash(user.PW, pw):
        return user
    return None
