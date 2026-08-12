'''
======================================================================
repositories/user_repository.py

User 테이블에 대한 DB쿼리만 담당하는 계층
"이메일이 중복이면 안됨" 같은 업무적인 판단은 여기서 하지 않는다.
여기서는 조회/저장만 한다. (DB관련)
======================================================================
'''
from sqlalchemy import select
from sqlalchemy.orm import Session
from models import User

class UserRepository:
    def __init__(self, session: Session):
        self.session = session

    def find_by_email(self, email: str) -> User | None:
        """
        로그인과 회원가입 중복체크 두 군데 모두에서 사용된다.
        이메일이 같으면 User반환, 결과가 없으면 None을 반환
        """
        stmt = select(User).where(User.email == email)
        # self.session.execute(stmt).scalar()
        return self.session.scalar(stmt)

    def find_by_id(self, user_id: int) -> User | None:
        stmt = select(User).where(User.id == user_id)
        return self.session.scalar(stmt)

    def save(self, user:User) -> User:
        self.session.add(user)
        self.session.commit()
        # 회원가입 직후에는 DB가 자동으로 채운 id, created_at값을 응답으로 돌려줘야 하는데, 
        # refresh()를 안 하면 그 값들이 아직 파이썬 객체에 반영 안된 상태일 수도 있어서
        self.session.refresh(user)
        return user