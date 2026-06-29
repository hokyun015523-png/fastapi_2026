#=======================================================================
# fastapi_review/routers/items.py
#  2026-06-29
#  item에 관한 엔드포인트 함수들
#
#  APIRouter: 미니 FastAPI처럼 동작하는 라우터 객체
#======================================================================

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
import crud, schemas
from dependencies import get_db

router = APIRouter(prefix='/items', tags=['items'])

@router.get('/',response_model=list[schemas.ItemResponse])
def read_items(skip: int=0, limit: int=100, db: Session=Depends(get_db)):
    return crud.get_items(db, skip=skip, limit=limit) #함수 호출 - 아이템 조회