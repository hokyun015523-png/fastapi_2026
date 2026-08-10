# ============================================================
# todo/jwt_create.py
#  
# - JWT를 실습해보는 연습용 스크립트
# - uv add jwt로 라이브러리 설치
# - Python에서 토큰을 생성하고 검증할 수 있도록 도와주는 라이브러리

# 헤더.페이로드.서명
# ============================================================
import jwt
from datetime import datetime, timedelta, timezone

# 서명(sing)에 사용할 비밀키 --> 이 키를 아는 사람만 "진짜" 토큰을 만들수 있고, 검증도 가능
SECRET_KEY = 'secret'

# 토큰에 담을 데이터 (payload, 페이로드)구성
payload = {
    'user_id':10,
    # exp(expiration): 이 토큰이 얼마까지 유효한지(10분 뒤 만료)
    'exp': datetime.now(timezone.utc) + timedelta(minutes=10),
}

# jwt.encode(payload, 비밀키, 알고리즘)--> payload를 Base64로 인코딩한 뒤, 비밀키로 
#                                         서명을 붙여 "헤더.페이로드.서명" 형태의 문자열 하나로 합쳐준다.
token = jwt.encode(payload, SECRET_KEY, algorithm='HS256')

print(token) # eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxMCwiZXhwIjoxNzg2MzQwOTM2fQ.QfsvrfNGZvkPMElTMqP_aLdqlLqkNe225FXA-amQZcY
