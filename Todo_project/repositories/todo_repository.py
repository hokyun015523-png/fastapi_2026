'''
======================================================================
repositories/todo_repository.py

todo테이블에 대한 DB쿼리만 담당하는 계층
쿼리 결과가 있으면 반환, 없으면 None(또는 빈 리스트) 반환까지만 책임지고,
그 이후 반응에 대한 것은 Service에게 넘긴다.

이렇게 나누는 이유: Repository는 DB에서 데이터를 가져오는 방법만 알면 되고,
    HTTPException 같은 웹(HTTP) 관련 개념을 몰라도 된다.
    나중에 이 프로젝트를 웹이 아닌 다른 방식으로도 사용하면 Repository만 그대로 재사용한다.
    Service/Router만 수정하면 된다.
======================================================================
'''
from sqlalchemy import select
from sqlalchemy.orm import Session
from models import Todo

class TodoRepository:
    def __init__(self, session: Session):
        # 세션을 생성자에서 미리 받아 인스턴스 변수(self.session)에 저장해둔다.
        #  아래 메서드들이 매번 session을 매개변수로 안 받아도 된다.
        self.session = session

    def find_all_by_user(self, user_id: int) -> list[Todo]:
        """
        특정 사용자의 Todo 전체를 조회한다.
        결과가 없으면 빈 리스트가 온다.
        """
        stmt = select(Todo).where(Todo.user_id == user_id)
        return list(self.session.execute(stmt).scalars().all())

    def find_by_id(self, todo_id: int, user_id: int) -> Todo | None:
        """
        todo_id와 user_id를 동시에 조건에 걸어서, "나의 Todo가 아니면 조회가 안되게 설정"
        찾으면 Todo 객체 반환, 못 찾으면 None 반환
        """
        stmt = select(Todo).where(Todo.id == todo_id, Todo.user_id == user_id)
        return self.session.execute(stmt).scalars().first()

    def save(self, todo: Todo) -> Todo:
        """
        새로 만든 Todo든, 기존 Todo를 수정하든 상관없이 저장한다.
        session.add() --> 이미 세션이 추적 중인 객체(수정된 기존 Todo)에 대해서는
            아무 일도 하지 않고 , 새 객체일 때만 의미가 있다.
        이 단점이 있어도 모두에서 같은 메서드를 사용할 수 있어 코드가 단순해진다.
        """
        self.session.add(todo)
        self.session.commit()
        return todo

    def delete(self, todo: Todo) -> None:
        self.session.delete(todo)
        self.session.commit()

