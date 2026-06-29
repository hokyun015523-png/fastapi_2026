#=======================================================================
# fastapi_review/schemas.py
#   2026-06-29
#   Pydandic 스키마 
#       공통 필드를 Base 클래스에 정의하고, Create/response가 상속 받는 구조
#           Item 스키마
#           User 스키마
#======================================================================

from pydantic import BaseModel
from typing import Optional

# Item 스키마
class ItemBase(BaseModel):
    title: str
    description: Optional[str] = None # 없어도 되는 필드, 작성한다면 문자열 / 기본값은 None

class ItemCreate(ItemBase):
    # 아이템 생성 시 클라이언트 보내는 데이터
    # title, description만 받는다. (id, owner_id는 서버가 자동 설정)
    pass

class ItemResponse(ItemBase):
    # 응답 시 클라이언트에게 돌려주는 데이터
    id: int # DB가 자동 생성한 id를 포함
    owner_id: int # 소유자 id 포함

    # 'from_attributes': True --> SQLAlchemy ORM객체를Pydantic 모델로 변환 허용
    model_config = {'from_attributes': True}

# User 스키마
class UserBase(BaseModel):
    email: str

class UserCreate(UserBase):
    # 회원가입 시 받는 데이터 : 이메링 + 평문 비밀번호
    # password는 DB에 그대로 저장되지 않는다 --> crud.py에서 해싱 후 저장
    password: str

class UserResponse(UserBase):
    # 유저 조회 응답 : 이메일 , id, 활성여부, 아이템 목록 포함
    id: int
    is_active: bool

    # items: 이 유저가 가진 item 목록을 보여준다(1:N 관계 결과)
    # 기본값 [] --> 아이템 없으면 빈 리스트로 응답
    items: list[ItemResponse] = []

    model_config = {'from_attributes': True}