# ========================================================================
# main.py
#
# 역할 : FastAPI 앱 정의 + CRUD 라우터 5개
#
# API목록
# GET /todos              --> 전체 할 일 조회
# GET /todos/{todo_id}    --> 단일 할일 조회
# POST /todos             --> 할 일 생성
# PATCH /todos/{todo_id}  --> 할 일 수정
# DELETE /todos/{todo_id} --> 할 일 삭제
# ========================================================================
from schema.response import TodoResponse
from schema.request import TodoCreateRequest, TodoUpdateRequest
from fastapi import FastAPI, status, HTTPException
from sqlalchemy import select # ORM 모델을 기준으로 조회 쿼리 객체를 생성
from database.db_connection import engine, SessionFactory
from database.orm import Base
from models import Todo

# 앱 시작 시 테이블 자동생성
# Base를 상속 받은 모든 모델 (Todo 등)의 테이블을 DB에 자동생성
# 이미 데이블이 있으면 건너뜀(데이터 삭제 안 함)
Base.metadata.create_all(bind=engine)

app = FastAPI()

# GET /Todos --> 전체 할 일 조회
@app.get(
    '/todos',
    response_model=list[TodoResponse], # 응답 형식 :  TodoResponse 리스트
    status_code=status.HTTP_200_OK # 성공 시 200 반환
)
def get_todos_handler():
    session = SessionFactory()
    try: # stmt : SQL문을 의미하는 atatement의 약자
        stmt = select(Todo) # 데이터를 조회하는 쿼리 객체(아직 데이터베이스에는 접근안했다)
        # session.execute(stmt) : 쿼리 객체를 실제 데이터베이스에 전달해서 실행
        # .scalars().all() : 실행 결과에서 테이블의 각 행에 대응되는 ORM객체를 추출해서 리스트로
        todos = session.execute(stmt).scalars().all() # 전체 결과 리스트로 반환
        return todos
    finally: # 예외가 발생하든 안하든 무조건 실행
        session.close()

# GET /todos/{todo_id} --> 단일 할 일 조회
@app.get(
    '/todos/{todo_id}',
    response_model=TodoResponse,
    status_code=status.HTTP_200_OK,
)
def get_todo_handler(todo_id: int):
    session = SessionFactory()
    try:
        stmt = select(Todo).where(Todo.id == todo_id)
        todo = session.execute(stmt).scalars().first() # 첫번째 결과 1개만
        if todo:
            return todo
        # 없으면 404 에러
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Todo not found'
        )
    finally:
        session.close()

# POST /todos --> 할 일 생성
@app.post(
    '/todos',
    response_model=TodoResponse,
    status_code=status.HTTP_201_CREATED # 생성 성공 시 201 반환
) 
def create_todo_handler(body: TodoCreateRequest): # 요청 body를 자동으로 파싱
    session = SessionFactory()
    try:
        # 요청 데이터로 Todo 객체 생성
        todo = Todo(
            title=body.title,
            is_done=body.is_done,
        )
        session.add(todo) # INSERT 준비
        session.commit() # DB에 실제 반영 (commit이 없으면 저장 안됨)
        return todo
    finally:
        session.close()

# PATCH /todos/{todo_id} --> 할 일 수정
@app.patch(
    '/todos/{todo_id}',
    response_model=TodoResponse,
    status_code=status.HTTP_200_OK
)
def update_todo_handler(todo_id: int, body: TodoUpdateRequest):
    session = SessionFactory()
    try:
        stmt = select(Todo).where(Todo.id == todo_id)
        todo = session.execute(stmt).scalars().first()
        if todo:
            # None이 아닌 값만 업데이트(부분 수정 가능)
            # title만 보내면 --> title만 수정,is_done만 보내면 is_done수정
            if body.title is not None:
                todo.title = body.title
            if body.is_done is not None:
                todo.is_done = body.is_done
            session.commit() # DB에 반영
            return todo  
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Todo not found'
        )
    finally:
        session.close()

# DELETE /todos/{todo_id} --> 할 일 삭제
@app.delete(
    '/todos/{todo_id}',
    status_code=status.HTTP_204_NO_CONTENT # 삭제 성공시 204(내용 없음)
)
def delete_todo_handler(todo_id: int):
    session = SessionFactory()
    try:
        stmt = select(Todo).where(Todo.id == todo_id)
        todo = session.execute(stmt).scalars().first()
        if todo:
            session.delete(todo) # DELETE 준비
            session.commit() # DB에 실제 반영
            return
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Todo not found'
        )
    finally:
        session.close()
