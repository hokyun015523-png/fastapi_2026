#=============================================
# fastapi_review/database.py
#   2026-06-29
#   DB 연결 설정
#
# pgAdmin --> database --> reviewdb 생성
#=============================================

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker

# PostgreSQL 연결
DATABASE_URL = 'postgresql+psycopg2://postgres:1234@localhost:5432/reviewdb'

#엔진 : DB와 실제로 연결되는 객체
engine = create_engine(DATABASE_URL)

# 새션 팩토리 : 트랜잭션(DB 작업) 단위를 만드는 공장
sessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base : 모든 ORM 모델이 상속받는 부모 클래스
#   Base를 상속한 클래스는 SQLAIchemy가 'DB테이블'로 인식한다
#   Base.metadata.create_all() 호출 시 Base를 상속한 모든 클래스를 테이블로 생성
Base = declarative_base()