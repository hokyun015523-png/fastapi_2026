# 간단한 메모장 만들기 --> DB 없이 메모리(리스트)만 사용 --> 컴퓨터를 다시 키면 데이터 초기화가 된다.
from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel
from datetime import datetime

app = FastAPI(
    title='메모장 API',
    description='FastAPI 입문 실습용 메모장 CRUD API',
    version='1.0.0'
)

# 임시 데이터 저장소(메모리)
memos = [] # memos라는 
next_id = 1 # 자동 증가 ID를 직접 관리(전역 변수)

#pydantic 모델 정의 : 메모 작성(생성), 메모 수정, 메모 보여주기
class MemoCreate(BaseModel):
    """POST 요청 바디- 메모 작성 시 받는 데이터"""
    content: str # 내용만 받는다.and

class MemoUpdate(BaseModel):
    """PATCH 요청 바디- None이 기본값 -> 보내지 않으면 기존 값 유지"""
    content: str | None = None

class MemoResponse(BaseModel):
    """응답으로 내보내는 메모 형태"""
    id: int
    content: str
    created_at: str # 생성 시간(메모를 만든 생성 시간)
    updated_at: str # 수정 시간(메모를 수정한 시간)


# 헬퍼 함수
def find_memo(memo_id: int):
    """ID로 메모를 검색 - 없으면 None을 반환"""
    return next((m for m in memos if m['id']==memo_id), None)  #  return nextm for m(3번) in memos if m['id']==memo_id), None

def now():
    """현재 시간을 보기 좋게 문자열로 반환"""
    return datetime.now().strftime('%Y-%m-%d %H:%M:%S')

# 엔드포인트
@app.get('/')
def home():
    """API 안내"""
    return {'message':'메모장 API입니다. /docs 에서 데스트해보세요'}

@app.get('/memos', response_model=list[MemoResponse])
def get_memos():
    """전체 메모 목록을 조회해주는 역할의 함수- 메모가 없다면 빈 리스트(list)를 반환"""
    return memos

@app.get('/memos/{memo_id}', response_model=MemoResponse)
def get_memo(memo_id: int):
    """특정 메모 1개 조회- memo_id로 조회, 없으면 404에러로 반환"""
    memo = find_memo(memo_id)
    if memo is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'{memo_id}번 메모를 찾을 수 없습니다.',
        )
    return memo

@app.post('/memos', response_model=MemoResponse, status_code=status.HTTP_201_CREATED)
def create_memo(body: MemoCreate):
    """새 메모 작성- 요청 바디:{'content':'메모내용'}""" 
    global next_id # 전역 변수 임을 선언 / glober-> 함수 안에서 밖에 있는 변수 값을 '변경/수정'하고 싶을 때 사용합니다.

    memo = {
        'id': next_id,
        'content': body.content,
        'created_at': now(),
        'updated_at': now(),
    }
    memos.append(memo)
    next_id += 1 # 다음 메모를 위해 1 증가

    return memo

@app.patch('/memos/{memo_id}', response_model=MemoResponse)
def update_memo(memo_id: int, body: MemoUpdate):
    """메모 수정(부분 수정)-content만 보내면 content만 수정, 
        updated_at은 수정 시각(자동 갱신)"""
    memo = find_memo(memo_id)
    if memo is None:
        raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f'{memo_id}번 메모를 찾을 수 없습니다.',
    ) #메모가번호가 없을때 예외 처리

    if body.content is not None:
        memo['content'] = body.content

    memo['updated_at'] = now() # 수정 시간 갱신

    return memo

@app.delete('/memos/{memo_id}', status_code=status.HTTP_204_NO_CONTENT) # / -> 이거는 경로
def delete_memo(memo_id: int):
    """메모 삭제 - 성공 204, 실패 404"""
    memo = find_memo(memo_id)
    if memo is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'{memo_id}번 메모를 찾을수 없습니다', 
        )

    memos.remove(memo)



