from fastapi import FastAPI

app = FastAPI()

# 서버 실행
@app.get('/')
def root_handler():
    return{'message':'hello, FastAPI'}

# 경로 사용
@app.get('/login') #get 요청과 경로 매핑 설정
def login_handler():
    return{'message':'로그인 페이지에 오신것을 환영합니다.'}

# 동적 경로 사용 --> /users/1, /users/2, ...처럼 사용자 아이디마다
# 별도의 경로를 정의할 필요 없이 하나의 경로 /users/{user_id} 를
# 정의 하여 동일한 패턴의 여러 요청에 대응할 수 있다.

# 경로 변수 사용
@app.get('/users/{user_id}')
def read_user_handler(user_id: int):
    return{'user_id':user_id, 'massage':f'사용자 {user_id} 정보 조회'}

# 쿼리 파라미터 사용
@app.get('/items')
def read_items_handler(max_price: int | None=None):
    # int일수도 있고, None일 수도 있으며, 기본값은 None으로 설정
    return{'max_price':max_price}
    
# 경로 변수와 쿼리 파라미터는 둘다 엔드포인트 함수의 매개변수로 사용된다.
# 경로 변수는 경로에서 값을 추출
# 쿼리 파라미터는 경로 뒤에 ?key=value 형태로 덧붙은 값을 추출