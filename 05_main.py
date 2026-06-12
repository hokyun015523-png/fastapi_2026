from schema.response import TodoResponse
from schema.request import TodoCreateRequest, TodoUpdateRequest
from fastapi import FastAPI, status, HTTPException

app = FastAPI()

# 임시 데이터 : 할 일 저장
todos = [
    {'id':1, 'title':'FastAPI 공부하기', 'is_done':False},
    {'id':2, 'title':'운동하기', 'is_done':True},
    {'id':3, 'title':'책 읽기', 'is_done':False},
]

# GET API : 전체 데이터 조회하기 (전체 할 일 조회)
@app.get(
    '/',
    response_model=list[TodoResponse],
    status_code=status.HTTP_200_OK
)
def get_todos_handler():
    return todos

# 단일 할 일 조회 (경로 변수)
@app.get(
    '/{todo_id}',
    response_model=TodoResponse,
    status_code=status.HTTP_200_OK
)
def get_todo_handler(todo_id: int):
    for todo in todos:
        if todo['id'] == todo_id:
            return todo
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Todo not found')

# 할 일 생성
@app.post(
    '/',
    response_model=TodoResponse,
    status_code=status.HTTP_201_CREATED
)
def create_todo_handler(body: TodoCreateRequest):
    new_todo = {
        'id': len(todos) + 1,
        'title': body.title,
        'is_done':body.is_done,
    }
    todos.append(new_todo)
    return new_todo  # 생성된(추가된) 데이터가 응답으로 반환된다.

# PUT --> 전체 수정, 모든 필드를 수정하는 방식. 
#           요청 본문의 데이터로 기존 데이터를 통째로 덮어쓴다.
#           요청 본문에 특정 필드가 누락되면 해당 필드의 기존 값이 사라질 수 있다.
# PATCH --> 부분 수정, 일부 필드만 수정하는 방식.
#           요청 본문에 포함된 항목만 변경하고, 나머지는 그대로 유지한다.

# 할 일 수정
@app.patch(
    '/{todo_id}',
    response_model=TodoResponse,
    status_code=status.HTTP_200_OK
)
def update_todo_handler(todo_id: int, body: TodoUpdateRequest):
    for todo in todos:
        if todo['id'] == todo_id:
            if body.title is not None:
                todo['title'] = body.title
            if body.is_done is not None:
                todo['is_done'] = body.is_done
            return todo
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Todo not found')

# 할 일 삭제
@app.delete(
    '/{todo_id}',
    status_code=status.HTTP_204_NO_CONTENT
)
def delete_todo_handler(todo_id: int):
    for todo in todos:
        if todo['id'] == todo_id:
            todos.remove(todo)
            return
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Todo not found')