# ==================================================
# football/main.py
# ==================================================
from fastapi import Depends, FastAPI, HTTPException         # 라이브러리불러오기
from sqlalchemy.orm import Session
from datetime import date

import crud, schemas                                        # 우리가 만든 모듈(파일) 불러오기
from database import SessionLocal

app = FastAPI()                                             # 묶기

# 종속성                                                     # 세션 넘기고, DB세션 닫기 
def get_db():
    """
    요청 하나하나마다 PostgrSQL 세션을 열고, 응답 후 닫아주는 의존성 함수
    """
    db = SessionLocal()
    try: 
        # yield 앞은 요청 처리 전에 실행되고, yield로 넘긴 db가 엔드포인트 함수에 주입된다. # 리턴이랑 비슷하다고 생각면됨.
        yield db
    finally:
        # 요청 처리가 끝나면 성공/실패와 관계 없이 DB세션을 닫는다.
        db.close()

@app.get('/')
async def root():
    """API 서버가 살아있는지 확인 하는 헬스체크 엔드포인트"""        
    return{"message": "API 상태 확인 성공"}

@app.get('/v0/players/', response_model=list[schemas.Player])
def read_players(skip: int = 0, limit: int = 100,
                minimum_last_changed_date: date = None,
                first_name: str = None,
                last_name: str = None,
                db: Session = Depends(get_db)):
    """선수 목록 조회

    skip / limit는 페이지네이션에 사용
    날짜 / 이름 조건은 선택 필터로 사용
    response_model은 SQLAlchempy ORM 객체를 Pydantic 응답 모델로 변환해준다.

    """
    players = crud.get_player(db, skip=skip, limit=limit,
                              minimum_last_changed_date=minimum_last_changed_date,
                              first_name=first_name,
                              last_name=last_name)
    return players

@app.get('/v0/players/{player_id}', response_model=schemas.Player)
def read_player(player_id: int,
                db: Session = Depends(get_db)):
    """player_id 하나로 특정 선수 상세 정보를 조회한다."""
    player = crud.get_player(db,player_id=player_id)
    if player is None:
        raise HTTPException(status_code=404, detail='선수를 찾을 수 없습니다.')
    return player