from sqlalchemy import *
from sqlalchemy.orm import relation, sessionmaker, DeclarativeBase, Mapped, mapped_column

import json
import requests

# internal API imports
import account

# create engine
class Base(DeclarativeBase):
    pass

engine = create_engine('''"dbms://user:pwd@host/dbname''', echo=True)
Base.metadata.create_all(engine)

Session = sessionmaker(autocommit=False, autoflush=False, bind=engine)
session = Session()

# test required
class QuizEntry(Base):
    __tablename__ = "Quiz"

    Quiz_Num: Mapped[int] = mapped_column(primary_key=True)
    Quiz_Body: Mapped[dict[str,Any]] = mapped_column(JSON)

    def __init__(self, Quiz_Num=0, Quiz_Body=""):
        self.Quiz_Num = Quiz_Num
        self.Quiz_Body = Quiz_Body
        
    def __repr__(self):
        return f"Quiz(Num: {Quiz_Num}, Body: {Quiz_Body})"
    
Base.metadata.create_all(engine)

# !! WIP !!
def Show(quiz_number):
    quiz = session.get(QuizEntry, quiz_number)
    raw_body = quiz.Quiz_Body

    # get request

# !! WIP !!
def Submit():
    

# !! WIP !!
def Check():
    '''TODO'''