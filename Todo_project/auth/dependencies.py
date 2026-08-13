'''
======================================================================
auth/dependencies.py

현재 로그인한 사용자의 id --> 라우터마다 반복하지 않도록 공용 의존성 함수를 정의

장점 
    1. 코드 중복 제거
    2. 토큰이 없으면 그냥 None으로 처리되던 보안 허점이 사라진다.
        HTTPBearer(기본값 auto_error=True) 가 토큰 자체가 없으면 자동으로 에러를 낸다.
        이 의존성을 통과했다는 것은 로그인이 확인되었다는 의미.
======================================================================
'''
from fastapi import Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from auth.jwt import decode_access_token

bearer = HTTPBearer()

def get_current_user_id(credentials: HTTPAuthorizationCredentials = Depends(bearer)) -> int:
    """
    Authorization 헤더에서 토큰을 꺼내고 검증하고, user_id만 반환한다.
    검증 실패(만료/위조/타입 불일치)는 decode_access_token 내부에서 이미 HTTPExcption을
    raise(강제 예외처리)하므로 여기서는 신경쓸 필요가 없다.
    """
    return decode_access_token(credentials.credentials)