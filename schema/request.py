from pydantic import BaseModel

# 할 일 생성 요청 모델
class TodoCreateRequest(BaseModel):
    title: str
    is_done: bool = False

# 할 일 수정 요청 모델
class TodoUpdateRequest(BaseModel):
    title: str | None = None
    is_done: bool | None = None