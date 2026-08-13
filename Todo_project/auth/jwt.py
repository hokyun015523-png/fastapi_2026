'''
======================================================================
auth/jwt.py

JWT 발급/검증 모듈

Access Token
Refresh Token

로그인 -> access_token + refresh_token 둘다 발급, refresh_token이 DB에 저장
30분 후 access_token 만료
할일 등록(POST), 할일 완료 체크(PATCH), 할일(GET)목적 --> 로그인 --> access_token 재발급
-> 목적 처리 완료 -> 처리완료 -> 로그아웃 access_token
시간이 많이 경과
refresh_token = None(초기화)
로그인 -> access_token + refresh_token 둘 다 재발급

왜 굳이 두개로 나눴는가 - Access_token 하남나 쓰면 딜레마가 생긴다
- 수명을 짧게 하면 -> 30분 마다 로그인해야 해서 불편함
- 수명을 길게하면 -> 탈취 당했을 때 오래 악용 가능하고, 서버가 저장 안하니 강제로 막을 방법도 없음
그래서 "자주 쓰지만 짧게 사는 access_token" + "가끔 쓰지만 오래 살고 DB에서 통제 가능한 refresh_token"으로
역할을 쪼갠것이다. Access_token은 탈취되어도 피개가 최대 30분으로 제한되고,
로그인 자체는 refresh_token 덕분에 7일간 끊기지 않는다.

payload에 들어있는 "type:" "access" / "type": "refresh" 필드가 두 토근을 구분하는 유일한 표식
이게 없으면 서버가 받은 토큰이 access용인지 refresh용인지 구별할 방법이 없어서,
누군가 refresh_token을 access_token 자리에 몰래 넣어 API를 계속 호출 하는 것도 막을 수 있다.
======================================================================
'''
import jwt # 라이브러리는 pyjwt(uv add pyjwt)
from datetime import datetime,timedelta,timezone
from fastapi import HTTPException, status

SECRET_KEY = 'your-secret-here'
ALGORITHM = 'HS256'

ACCESS_TOKEN_EXPIRE_MINUTES = 30 # 자주 쓰이는 토큰이나 짧게(30분)
REFRESH_TOKEN_EXPIRE_DAYS = 7 # 재로그인 없이 버틸 수 있는 기간(7일)

def _create_token(user_id: int, token_type: str, expires_delta: timedelta) -> str:
    """
    Access/Refresh 토큰 생성(user_id, 만료시간, 서명)
    공통 부분을 내부 함수로 정의

    이름 앞 _(언더스코어)의 역할 --> 이 파일 밖에서는 직접 부르지 말고, 아래 두 함수를 통해서만 
    호출해라 라는 파이썬의 관례

    """
    payload = {
        "user_id": user_id,
        "type": token_type, # Access/Refresh으로 나눠짐
        "exp": datetime.now(timezone.utc) + expires_delta,
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

def create_access_token(user_id: int) -> str:
    return _create_token(user_id, 'access',timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))

def create_refresh_token(user_id: int) -> str:
    return _create_token(user_id, 'refresh', timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS))

def decode_token(token: str, expected_type: str) -> int:
    """
    토큰을 검증하고 user_id를 반환한다.
    expected_type을 반드시 넘겨받아서, access 토큰인데 refresh 자리에 사용했다 같은 오남용을 
    여기서 걸러낸다.(핵심 보안 포인트)
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM]) # 서명 검증 + payload 복원
    except jwt.ExpiredSignatureError: # 토큰이 만료된 경우
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Token expired')
    except jwt.InvalidAlgorithmError: # 그 외 나머지 토큰 오류(ex.서명 불일치, 형식 오류 등)
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Invalid token')

    if payload.get('type') !=expected_type: # refresh token 을 access token 자리에 몰래 써서 일반 API를 호출하려는 시도를 막아준다
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f'{expected_type} 토큰이 필요합니다.'
        )

    return payload['user_id'] # 서명 검증 + 타입 검사를 모두 통과하면 user_id만 반환

# 기존 코드를 건드리지 않고 기능을 확장하는 방법은 하나
def decode_access_token(token: str) -> int:
    return decode_token(token, expected_type='access')