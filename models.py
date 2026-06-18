# ==============================================================
# models.py
# - SQLAlchemy ORM 모델 정의 파일
# - 파이썬 클래스 ↔ DB 테이블 --> 매핑(mapping)하는 부분
# - Todo(할 일) 1개는 User(회원) 1명에게 속할 수 있다 --> 1:N 관계
#       (한 명의 회원이 여러 개의 할 일을 가질 수 있다.)

# 기본키(Primary Key, PK)
# - 테이블에서 각 행(row)을 고유하게 식별하기 위한 컬럼
# - 기본키 값은 절대 중복될 수 없다.
# - 반드시 하나의 값이 존재해야 한다.
# - 테이블 내부에서 데이터를 구분하기 위한 기준

# 외래키(Foreign Key, FK)
# - 다른 테이블의 기본키를 참조하는 컬럼
# - 한 테이블의 데이터가 다른 테이블의 어떤 데이터와 연결되었는지를 표현하기 위해 사용된다.
# - ex.이를 통해 각 할 일이 어떤 사용자에게 속하는 지 알 수 있다.
# - 테이블과 테이블 사이 관계를 표현하기 위한 연결 고리
# ==============================================================

from datetime import datetime
from sqlalchemy import Integer, String, Boolean, ForeignKey, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from database.orm import Base 

# --- Todo 모델 (할 일 테이블) -----------------------------
class Todo(Base):
    __tablename__ = 'todos'  # 실제 DB에 생성할 테이블 이름

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,  # 기본키 - 각 행(row)을 구분하는 고유값
        autoincrement=True, # 새 행이 추가될 때마다 1씩 자동 증가
    )
    title: Mapped[str] = mapped_column(
        String(255),
        nullable=False, # NULL(빈 값) 불가 - 할 일 제목은 반드시 입력해야 한다
    )
    is_done: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,   # 새로 생성될 때 기본값은 '완료안함'
    )    
    user_id: Mapped[int] = mapped_column(
        ForeignKey('user.id'),  # user 테이블의 id컬럼을 참조하는 외래키(FK)
        nullable=True,   # 담당 회원을 지정하지 않고도 할 일 생성 가능(선택 사항)
    )    
    # 관계(relationship) 설정 - todo.user로 연결된 User 객체에 바로 접근 가능해진다.
    user: Mapped['User'] = relationship(
        back_populates='todos', # User쪽의 todos 속성과 서로 짝지어진다.(양방향 관계)
    )    


# --- User 모델 (회원 테이블) ---------------------------------------
class User(Base):
    __tablename__ = 'user'

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(
        String(255),
        unique=True,  # 같은 이메일로 중복 가입 불가
        index=True,   # 이메일로 조회가 자주 일어날 것이므로 검색 속도 향상을 위한 인덱스
        nullable=False, 
    )
    hashed_password: Mapped[str] = mapped_column(
        String(255),
        nullable=False, # 비밀번호는 평문(일반언어)이 아닌 '해시된 값'으로 저장
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=func.now(),  # 행이 추가되는 시점에 DB가 자동으로 현재 시간을 채워준다.
        nullable=False,
    )        
    # 한 명의 회원은 여러 개의 todo를 가질 수 있다. (리스트로 표현)
    todos: Mapped[list['Todo']] = relationship(
        back_populates='user', # Todo모델의 user속성과 양방향으로 연결하라
        # all --> 추가(add), 삭제(delete), 병합(merge) 등 대부분의 동작을 부모(User)에서
        #           자식(Todo)으로 연쇄적으로 적용해라
        cascade='all, delete-orphan',  # 회원이 삭제되면 그 회원의 Todo들도 함께 자동 삭제된다.
    )    