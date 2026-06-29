#=======================================================================
# fastapi_review/crud.py
#   2026-06-29
#  DB 조작 함수
#
# CRUD --> 데이터를 다루는 4가지 기본 동작
#          Create: 생성 POST(FastAPI) INSERT(SQL)--> ex.회원가입, 글 작성
#          Read : 조회 GET(FastAPI) SELECT(SQL) --> ex.목록보기, 상세보기
#          Update: 수정 PUT/PATCH(FastAPI) UPDATE(SQL) --> ex.정보 수정
#          Delete: 삭제 DELETE(FastAPI) DELETE(SQL) --> ex.회원 탈퇴, 글 삭제
#======================================================================

from sqlalchemy.orm import Session
from pwdlib import PasswordHash
import models, schemas # fastapi_review/안에 있는 파일들 models.py, schemas.py

pwd_hasher = PasswordHash.recommended() # pwdlib이 권장하는 해싱 알고리즘(argon2) 자동 선택

# User CRUD
def get_user(db:Session, user_id: int):
    # db.query(모델): 해당 테이블 전체를 대상으로 쿼리 시작
    # .filter(조건): WHERE 절 --> users.id = user_id
    # .first(): 첫번째 결과 하나만 반환. 없으면 None을 반환
    return db.query(models.User).filter(models.User.id == user_id).first()

def get_user_by_email(db: Session, email: str):
    # 이메일로 유저 조회 --> 회원 가입할때 중복 가입여부 확인
    return db.query(models.User).filter(models.User.email == email).first()


def get_users(db: Session, skip: int = 0, limit: int = 100):
    # .offset(skip): 앞에서 skip개 건너뜀 
    # (페이지네이션 때문에 사용 / 데이터를 한번에 다 보여주지 않고 페이지 단위로 나눠서 보여주는 것)
    # .limit(limit): 최대 limit개만 반환
    # .all(): 조건에 맞는 전체 결과를 리스트로 반환
    return db.query(models.User).offset(skip).limit(limit).all()

def create_user(db: Session, user: schemas.UserCreate):
    # 평문 비밀번호(user.Password)를 해싱(원래의 값을 알 수 없는 암호화된 문자열로 변환)하여 저장
    hashed_password = pwd_hasher.hash(user.password)

    # ORM 객체 생성 (아직DB에 저장 안됨)
    db_user = models.User(email=user.email, hashed_password=hashed_password)

    # db. add(): 세션에 객체 추가 (INSERT준비)
    db.add(db_user)

    db.commit() # 실제 DB에 INSERT 실행(이 시점에 저장된다.)

    db.refresh(db_user) # DB가 자동 생성한 id등의 값을 객체에 다시 패워 넣는다.

    return db_user

# Item CRUD
def get_items(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Item).offset(skip).limit(limit).all()

def create_user_item(db: Session, item:schemas.ItemCreate, user_id: int):
    # item.model_dump(): Pydantic 객체 -> 딕셔너리로 변환 {'title':..., 'description':....}
    # **item.model_dump(): 딕셔너리를 키워드 인자로 언팩
        # *args: 튜플형태로 묶는다
    # owner_id=user_id: 클라이언트가 직접 입력하지 않고 서버가 주입(보안)
    
    db_item = models.Item(**item.model_dump(), owner_id=user_id)
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
  
    return db_item