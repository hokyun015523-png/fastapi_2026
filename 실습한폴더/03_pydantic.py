# pydantic 라이브러리
# --> 데이터 검증 + 데이터 모델 정의 -> 외부 라이브러리(설치)
# --> BaseModel 을 상속하여 스키마기반 데이터구조를 정의한다.
# --> 타입 힌트를 단순 문서 수준이 아니라 런타임에서 실제 검사까지 해준다.
# --> 일부 프레임워크에서 요청/응답 검증에 필수적 이다.
from pydantic import BaseModel

class User(BaseModel):
    id: int
    name: str
    email: str

# 자동으로 타입 변환 및 검증
user = User(id='1', name='홍길동', email='test@example.com')
print(user)

user2 = User(id='a', name='메시', email='siuuuu@example.com')
print(user2)

# 왜 pydantic을 사용하는가?
# --> 외부 입력 (사용자메세지, API응답, DB 검색 결과 등)을 많이 다루는데,
#       잘못된 데이터가 들어올 수 있다.
#       예외(에러) 발생 시 안전하게 처리가능하다.
# --> 실제 값이 규칙에 맞는지 확인하고 필요하면 변환까지 해주는 도구
# --> 검증기

# BaseModel ?
# pydantic의 기본 클래스
# --> 우리가 만드는 데이터 클래스(모델)의 뼈대(스키마)를 정의할 때 사용한다
# --> 타입 힌트 기반으로 자동검증, 데이터 입력시 자동 변환 기능이 있다.