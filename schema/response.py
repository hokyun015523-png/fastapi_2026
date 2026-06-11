from pydantic import BaseModel

# 할 일 응답 모델
class TodoResponse(BaseModel):
    id: int
    title: str
    is_done: bool