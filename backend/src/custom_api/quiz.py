# external API imports
import os

from sqlalchemy import *
from sqlalchemy.orm import relationship, sessionmaker, DeclarativeBase, Mapped, mapped_column

import json

from flask import Flask, request, jsonify

app = Flask(__name__)

# internal API imports
import account

# create engine
class Base(DeclarativeBase):
    pass

DATABASE_URL = os.environ.get(
    "DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/mockinvest"
)

engine = create_engine(DATABASE_URL, echo=True)
Session = sessionmaker(autocommit=False, autoflush=False, bind=engine)
session = Session()

class QuizEntry(Base):
    __tablename__ = "Quiz"

    Quiz_Num: Mapped[int] = mapped_column(primary_key=True)
    Quiz_Body: Mapped[dict[str,Any]] = mapped_column(JSON, nullable=True)
    Quiz_Answer: Mapped[int] = mapped_column(Integer)

    def __init__(self, Quiz_Num=0, Quiz_Body=""):
        self.Quiz_Num = Quiz_Num
        self.Quiz_Body = Quiz_Body
        
    def __repr__(self):
        return f"Quiz(Num: {Quiz_Num}, Body: {Quiz_Body})"

# ----------------------------------------------------------------------
# Core APIs 
# ----------------------------------------------------------------------

with open('data/quiz.json', 'r', encoding='utf-8') as f:
    data = json.load(f)
    quiz = data.get('quiz', [])



# ----------------------------------------------------------------------
# Core APIs 
# ----------------------------------------------------------------------

def Show(quiz_num):
    quiz = session.get(QuizEntry, quiz_num)
    if not quiz:
        raise ValueError

    try:    
        return quiz.Quiz_Body
    except ValueError as e:
        return None

def Check(quiz_num, user_answer):
    quiz = session.get(QuizEntry, quiz_num)
    if not quiz: 
        raise ValueError
    
    try:
        if user_answer == quiz.Quiz_Answer:
            return True
        else:
            return False
    except ValueError as e:
        return None

if __name__ == '__main__':
    app.run(debug=True, port=5000)