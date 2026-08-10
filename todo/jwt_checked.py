# ============================================================
# todo/jwt_checked.py
#  
# - "서명이 왜 중요한지" 확인하는 실습 스크립트
# - 올바른 키로 검증 성공 / 잘못된 키로 검증 실페 --> 두 경우를 다 비교
# ============================================================
import jwt
from datetime import datetime, timedelta, timezone

SECRET_KEY = 'secret'
BAD_SECRET = 'wrong-secret' # 잘못된 키

payload = {
    'user_id': 10,
    'exp': datetime.now(timezone.utc) + timedelta(minutes=1),
}

# 정상적인 비밀키로 토큰 생성
token = jwt.encode(payload, SECRET_KEY, algorithm='HS256')
print(f'token: {token}')

# # 정상적인 비밀키로 검증 + 성공
decoded = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
print(f'OK: {decoded}')

# 잘못된 비밀키로 검증 -> 서명 불일치로 실패해야 정상
try:
    jwt.decode(token, BAD_SECRET, algorithms=['HS256'])
except jwt.InvalidSignatureErro:
    print('Singnature 검증 실패: 잘못된 secret')