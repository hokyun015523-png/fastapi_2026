'''
======================================================================
schema/response.py

서버가 클라이언트(사용자)에게 "돌려주는" 데이터의 형태를 정의하는 파일
request.py와 분리하는 이유: 회원가입이 경우 "요청"에는 password가 있지만, 
    "응답"에는 절대 포함하면 안되기 때문이다 (보안사고 방지)
======================================================================
'''
from datetime import datetime
from pydantic import BaseModel

# --- 할 일 응답 모델 --------------------------
class TodoResponse(BaseModel):
    id: int
    title: str
    is_done: bool
    # "이 할 일이 누구의 것인지"를 클라이언트가 화면에서 구분할 수 있도록 cnrk
    user_id: int | None

# ---회원가입 응답 모델 ---------------------------
# pydantic이 password를 필터링 시켜 제외
class UserSignUpResponse(BaseModel):
    id: int
    email: str
    created_at: datetime
