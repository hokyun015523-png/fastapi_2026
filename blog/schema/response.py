from pydantic import BaseModel

# GET 응답 모델 - 게시글 (아티클) 조회
class ArticleResponse(BaseModel):
    id: int
    title: str
    content: str

    