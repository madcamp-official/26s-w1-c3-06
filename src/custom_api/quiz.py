from sqlalchemy import *
from sqlalchemy.orm import relation, sessionmaker, DeclarativeBase, Mapped, mapped_column

import json

# internal API imports
import account

# create engine
class Base(DeclarativeBase):
    pass

engine = create_engine('''"dbms://user:pwd@host/dbname''', echo=True)
Base.metadata.create_all(engine)

Session = sessionmaker(autocommit=False, autoflush=False, bind=engine)
session = Session()

# !! WIP !!
class QuizEntry(Base): ''' align with post 2.0 syntax'''
    __tablename__ = "Quiz"

    Quiz_Num: Mapped[int] = mapped_column(primary_key=True)
    Quiz_Body: Mapped[dict[str,Any]] = mapped_column(JSON)

    # default profile is embedded in website
    def __init__(self, Quiz_Num=0, Quiz_Body=""):
        self.Quiz_Num = Quiz_Num
        self.Quiz_Body = Quiz_Body
        
    def __repr__(self):
        return f"Quiz({Quiz_Num}, {Quiz_Body})"
    
