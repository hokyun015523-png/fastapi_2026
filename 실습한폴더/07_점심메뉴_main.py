# 오늘 점심 뭐 먹지?? - 점심메뉴추천 API
from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel
import random

app = FastAPI(
    title='점심 메뉴 추천 API',
    description='오늘 뭐 먹을지 고민될 때 사용하는 메뉴 추천 API입니다!',
    version='1.0.0',
)

# 임시 데이터 장소
menus = [
    {'id':1, 'name':'김치찌개', 'category':'한식', 'price':9000, 'like':0},
    {'id':2, 'name':'돈까스', 'category':'일식', 'price':11000, 'like':0},
    {'id':3, 'name':'마라탕', 'category':'중식', 'price':1300, 'like':0},
    {'id':4, 'name':'햄버거', 'category':'양식', 'price':8500, 'like':0},
]

# 요청 바디(Body) 스키마 정의 - Pydantic 모델
class MenuCreateRequest(BaseModel):
    """메뉴 생성 시 클라이언트가 내보내는 데이터 구조"""
    name: str
    category: str
    price: int

class MenuUpdateRequest(BaseModel):
    name: str | None = None
    category: str | None = None
    price: int | None = None

# 엔드포인트 정의
@app.get('/')
def home():
    """루트 경로 - API 안내메시지 반환"""
    return {'message':'오늘 뭐 먹지? 점심 메뉴 추천 API입니다.'}

@app.get('/menus')
def get_menus():
    """전체 메뉴 목록 반환
    GET /menus
    응답: 메뉴 리스트 전체
    """
    return menus

@app.get('/menus/random')
def random_menu():
    """랜덤 메뉴 1개 반환
    GET /menus/random
    주의: 반드시 특정 id메뉴 반환보다 위에 정의되어야 한다.
    """
    return random.choice(menus)  # random.choice() - 선택한다.

@app.get('/menus/{menu_id}')
def get_menu(menu_id: int):
    """특정 ID의 메뉴 1개 반환
    GET /menus/1
    없는 아이디라면 404 반환
    """
    for menu in menus:
        if menu['id'] == menu_id:
            return menu
    raise HTTPException(status_code=404, detail='메뉴를 찾을 수 없습니다!')

@app.post('/menus', status_code=status.HTTP_201_CREATED)
def create_menu(body: MenuCreateRequest):
    """새 메뉴 등록
    POST /menus
    body: name, category, price를 전달
    id: 자동 부여 (+1)
    like: 생성 시 항상 0으로 초기화
    """
    new_menu = {
        'id': len(menus) + 1,
        'name': body.name, 
        'category': body.category,
        'price': body.price,
        'like': 0,
    }
    menus.append(new_menu)
    return new_menu

@app.patch('/menus/{menu_id}')
def update_menu(menu_id: int, body: MenuUpdateRequest):
    """특정 메뉴 부분 수정
    PATCH /menus/1
    전달된 필드만 수정, 나머지는 기존 값 유지
    """
    for menu in menus:
        if menu['id'] == menu_id:
            if body.name is not None:
                menu['name'] = body.name
            if body.category is not None:
                menu['category'] = body.category
            if body.price is not None:
                menu['price'] = body.price
            return menu
    raise HTTPException(status_code=404, detail='메뉴를 찾을 수 없습니다!')

@app.patch('/menus/{menu_id}/like')
def like_menu(menu_id: int):
    """메뉴 좋아요+1
    PATCH /menus/1/like
    요청 바디가 없다. url만으로 동작
    like 필드를 1증가시키고, 수정된 메뉴 반환
    """
    for menu in menus:
        if menu['id'] == menu_id:
            menu['like'] += 1
            return menu
    raise HTTPException(status_code=404, detail='메뉴를 찾을 수 없습니다 ㅠㅠ')

@app.delete('menus/{menus_id}', status_code= status.HTTP_204_NO_CONTENT)
def delete_menu(menu_id: int):
    """ 특정 메뉴 삭제
    DELETE /menus/1
    """
    for menu in menus:
        if menu['id'] == menu_id:
            menus.remove(menu)
            return
    raise HTTPException(status_code=404, detail='메뉴를 찾을 수 없습니다.')

@app.delete('menus/{menus_id}', status_code= status.HTTP_204_NO_CONTENT)
def delete_menu(menu_id: int):
    """ 특정 메뉴 삭제
    DELETE /menus/1
    """
    for menu in menus:
        if menu['id'] == menu_id:
            menus.remove(menu)
            return
    raise HTTPException(status_code=404, detail='메뉴를 찾을 수 없습니다.')