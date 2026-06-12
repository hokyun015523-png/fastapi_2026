from fastapi import FastAPI, status
from pydantic import BaseModel

app = FastAPI()

# http://localhost:8000/
# http://127/0.0.1:8000

#1. 기본 GET 엔드포인트 - 파라미터 없음
@app.get('/')
def root_handler():
    #리턴되는 자료형은 dict -->변환, 자동으로 json으로 변환해서 응답
    return {'message':'hell0, FastAPI'}

# 2. 추가 경로 =파라미터 없음
@app.get('/login')
def login_handler():
    return {'message':'로그인 페이지에 오신걸 환영합니다.'}

# 3.경로 변수(Path Parameter)
# url의 일부를 변수를 받는다 ->> {변수명} 사용
@app.get('/users/{user_id}')
def read_user_handler(user_id: int): # 타입 힌트
    return{'user_id':user_id, 'message':f'사용자 {user_id} 정보조회'}

# 4. 쿼리 파라미터(Query Parameter)
# url 뒤 ?key=value 형태로 전달
# max_price: int | None = None -> int 또는 None이 올 수 있다 -->Optional[int] 과 동일
@app.get('/items')
def read_items_handler(max_price: int | None = None): # 초기값을 None으로 먼저 넣어 놓는다
    return {'max_price': max_price}

# 5.pydantic 모델 - 요청/응답 데이터 구조 정의
class Item(BaseModel):
    name: str
    price: int
    is_stock: bool = True # 기본값을 True로 넣었다.(요청 시 생략 가능)

# 6. POST - 요청 본문(Request Body) 수신
@app.post(path='/items',
          response_model=Item, # 응답 구조를 Item으로 고정)
          status_code=status.HTTP_201_CREATED
)
def create_item_handler(item:Item):
    return item

# 7.PUT -경로 변수 + 쿼리 파라미터 +요펑 본문 혼합
# FastAPI가 파라미터 종류를 자동으로 구분하는 규칙
#   {item_id} --> 경로 변수(url에 중괄호로 선언)
#   assignee --> 쿼리 파라미터(단순 타입이고 경로에 없음)
#   item:Item --> 요청 본문(pydantic 모델이면 Body)

# 요청 PUT
# http://localhost:8000/items/5?assignee=홍길동
# Body
#   {'name:'마우스', 'price':30000}
# 
@app.put('/item/{item_id}')
def update_item_handler(item_id: int, assignee: str, item: Item):
    return {
        'item_id' : item_id,
        'assignee': assignee, #담당자
        'item':item
    }

# 8.응답 모델 (Response Model)
# 반환되는 데이터를 OrderResponse 형태로 필터링
# 서버 내부에서 민감 데이터(비밀번호 등)가 dict에 섞여 있어도
# response_model에 정의된 필트만 클라이언트에 전달 된다. --> 보안
class OrderResponse(BaseModel):
    order_id: int
    pickup: bool | None = None # 없으면 null반환

# GET
@app.get('/orders/{order_id}', response_model=OrderResponse)
def get_order_handler(order_id: int, pickup: bool | None = None):
    return { 
        'order_id':order_id,
        'pickup': pickup # bool 쿼리파라미터 ?pickup= true / ?pickup=1 /pickup=yes
    }