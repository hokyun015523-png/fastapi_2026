#=============================================
# fastapi_review/models.py
#   2026-06-29
#   ORM 모델(1:N 관계)
#=============================================

from sqlalchemy import Boolean, Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from database import Base

class User(Base):
    # class이름과 실제 DB에 생성될 테이블 이름은 달라도 된다.
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, index=True) # 기본키, 인덱스 생성 후 검색 속도 증가
    email = Column(String(100), unique=True, index=True) # 같은  메일로 중복 가입 불가
    hashed_password = Column(String(200)) # 비밀번호는 평문이 아닌 해시값으로 저장(보안)
    is_active = Column(Boolean, default=True) # 계정 활성화 여부(가입 즉시 활성화)

    # 1 : N 관계 설정
    # back_populates='owner' --> Item의 owner속성과 서로 연결된다
    # user.items --> 해당 유저의 아이템 목록 반환
    items = relationship('Item', back_populates='owner')

class Item(Base):
    __tablename__ = 'items'

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(100), index=True)
    # nullable=True --> 값이 없어도 된다, 기본값이 True (생략 가능)
    description = Column(String(300), nullable=True)

    # 외래키(FK) -->  items.owner_id 컬럼이 user.id를 참조
    #                이  아이템이 어느 유저 것인지 연결하는 실제 컬럼
    #                owner_id에 없는 users.id 값을 넣으면 DB에서 오류 발생(무결성 보장)
    owner_id = Column(Integer, ForeignKey('users.id'))

    # 역참조(back reference) --> 관계의 반대방향으로 접근하는것
    # User 클래스의 items 속성과 owner를 서로 연결
    # --> User의 items와 Item의 owner가 한쌍을 이룬다.
    owner = relationship('User', back_populates='items')