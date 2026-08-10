# ============================================================
# todo/auth/jwt.py
#  
# - JWT(JSON Web Token) 발급과 검증을 담당하는 모듈
# - 실제 로그인 기능에 사용(인코딩, 디코딩, 서명 검증)
# ============================================================
import jwt
from datetime import datetime, timedelta, timezone
from fastapi import HTTPException, status

SECRET_KEY = 'your-secret-here'
ALGORITHM = 'HS256' # HMAC-SHA256 서명 알고리즘

def create_access_token(user_id: int, expires_minutes: int) -> str:
    """
    로그인에 성공한 사용자의 id를 담아 토큰 문자열을 발급한다.
    """
    payload = {
        'user_id': user_id, 
        'exp': datetime.now(timezone.utc) + timedelta(minutes=expires_minutes),
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
def decode_access_token(token: str) -> int:
    """
    토큰을 검증하고, 그안에 담겨있던 user_id만 뽑아서 반환한다.
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload['user_id']
    except jwt.ExpiredSignatureError:
        # 서명은 정상인데 exp(만료시간)이 지난 경우
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Token expired'
        )
    except jwt.InvalidTokenError:
        # 서명이 위조되었거나 토큰 형식 자체가 문제인 경우
        # (만료 시간을 제외한 모든 문제를 처리한다.)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Invalid token'
        )