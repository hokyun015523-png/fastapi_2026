'''
======================================================================
Todo_prject/main.py

FastAPI 애플리케이션의 진입점 (entry point)
JWT 인증 토큰 방식으로 진행
======================================================================
'''
from fastapi import FastAPI
from database.db_connection import engine
from database.orm import Base
from routers.todo import router as todo_router
from routers.user import router as user_router
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(_):
    # 앱 시작시 1회 실행: models.py에 정의된 테이블들을 DB에 생성
    # (이미 테이블이 있으면 아무일도 하지 않는다.)
    Base.metadata.create_all(bind=engine)
    yield

# FastAPI 앱 객체 생성
# lifespan에 위에 만든 함수를 연결해서 "서버 켜질 때 테이블 자동 생성"이 실제로 작업
app = FastAPI(lifespan=lifespan)

# routers\todo.py, routers\user.py에서 만든 라우터를 app하나에 "합체"시키는 부분
app.include_router(todo_router)
app.include_router(user_router)