from pydantic import BaseModel

# POST 생성 요청 모델 -> 게시글(아티클)
class ArticleRequest(BaseModel):
    title: str
    content: str


# PATCH 수정 요청 모델 - 게시글 (아티클)
class ArticleUpdateRequest(BaseModel):
    title: str | None = None
    content: str | None = None

    
