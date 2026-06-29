#=======================================================================
# fastapi_review/main.py
#  2026-06-29
#  라우터를 등록 - 실행
#======================================================================

from fastapi import FastAPI
from database import engine
import models
from routers import users, items

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

# include_router(): 라우터를 앱에 등록 (플러그인 꽂기)
#   users.router안의 모든 엔드포인트가 app에 연결
#   기능이 늘어나도 이 파일에는 include_router() 한 줄씩만 추가하면 된다.
app.include_router(users.router)
app.include_router(items.router)
