'''
======================================================================
repositories/todo_service.py

Todo 관련 "업무 규칙"을 담당하는 계층
DB 쿼리 자체는 직접하지 않고, TodoRepository에게 다 위임한다.
없으면 "404에러를 낸다." 수정할 때 "title/is_done만 부분 반영한다" 등의 판단들을 정의
이 파일은 FastAPI의 요청/응답 객체를 직접 다루지 않는다. ()
======================================================================
'''
from fastapi import HTTPException, status
from models import Todo
from repositories.todo_repository import TodoRepository
from schema.request import TodoCreateRequest, TodoUpdateRequest

class TodoService:
    def __init__(self, repository: TodoRepository):
        self.repository = repository

    def get_todos(self, user_id: int) -> list[Todo]:
        # Repository 호출을 그대로 전달하기만 하느 메서드
        # 추가 기능은 "완료된 것만 보기" 같은 필터 옵션이 추가된다면 그 판단이 여기에 들어간다
        # Router가 Repository를 직접 알 필요가 없다는 구조 자체를 보여준다.
        return self.repository.find_all_by_user(user_id)

    def get_todo(self, todo_id: int, user_id: int) -> Todo:
        # 없으면 404라는 업무 판단을 한다.
        # Repository에서 None을 반환 -> 404 에러(에러를 낼지 통과를 시킬지는 이 계층에서 처리)
        todo = self.repository.find_by_id(todo_id, user_id)
        if todo is None:
            raise HTTPException(status.HTTP_404_NOT_FOUND, detail='Todo not found')

        return todo

    def create_todo(self, body: TodoCreateRequest, user_id: int) -> Todo:
        todo = Todo(title=body.title, is_done=body.is_done, user_id=user_id)
        return self.repository.save(todo) # DB에 저장(서비스가 바로 저장 X -> 레파지토리한테 맡긴다)
    
    def update_todo(self, todo_id:int, body: TodoUpdateRequest, user_id: int) -> Todo:
        todo = self.get_todo(todo_id,user_id)
        if body.title is not None: # 수정할 데이터가 있다면
            todo.title = body.title # 할일 수정
        if body.is_done is not None:
            todo.is_done = body.is_done # 할일 완료/미완료 수정
        return self.repository.save(todo) # DB에 저장(서비스가 바로 저장 X -> 레파지토리한테 맡긴다)

    def delete_todo(self, todo_id: int, user_id: int) -> None:
        todo = self.get_todo(todo_id, user_id) # 삭제할 할일 목록을 찾아온다
        self.repository.delete(todo)