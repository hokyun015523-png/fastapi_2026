from pydantic import BaseModel
from datetime import datetime

# 할 일 응답 모델
class TodoResponse(BaseModel):
    id: int
    title: str
    is_done: bool

# 회원가입 응답 모델
class UserSignUpResponse(BaseModel):
    id: int
    email: str
    created_at: datetime