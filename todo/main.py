# ==============================================================================
# mian.property
# FastAPI 애플리케이션의 진입점(entry point)
# - 앱(app) 객체 생성, DB 테이블 생성, 라우터(Router) 등록을 담당하는 파일
# ==============================================================================
from fastapi import FastAPI
from database.db_connection import engine
from database.orm import Base
from routers.todo import router as todo_router # 할 일(Todo) 관련 API 라우터
from routers.user import router as user_router # 회원가입/사용자 관련 API라우터 

Base.metadata.create_all(bind=engine)

app = FastAPI() # 우리가 만드는 서버 그 자체

# 라우터 등록
app.include_router(todo_router)
app.include_router(user_router)