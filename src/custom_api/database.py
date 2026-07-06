import os

from sqlalchemy import *
from sqlalchemy.orm import relation, sessionmaker, DeclarativeBase, Mapped, mapped_column

from flask import Flask, request, jsonify

'''
db = SQLAlchemy()

def init_db(app):
    # 2. 데이터베이스 URI 설정 (사용자, 비밀번호, 호스트, DB이름 입력)
    # 예: 'postgresql://username:password@localhost:5432/mydatabase'
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'postgresql://user:pass@localhost:5432/db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # 3. 앱에 데이터베이스 바인딩
    db.init_app(app)
    
    # 4. 테이블 자동 생성 (필요시 사용)
    with app.app_context():
        db.create_all()
        
SQLALCHEMY_DATABASE_URL = "sqlite:///./sql_app.db"