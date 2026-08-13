'''
======================================================================
schema/request.py

클라이언트가 서버로 보내는 데이터의 형태를 정의하는 파일
Pydantic BaseNodel을 상속하면 FastAPI가 요청 body를 자동으로 검증해준다.
    --> 타입이 안 맞거나 필수값이 없으면 자동으로 422 에러 응답
======================================================================
'''
import re # 정규표현식 --> 문자열이 특정 패턴을 포함하는지 검사
from pydantic import BaseModel, EmailStr, Field, field_validator

# --- 할 일을 생성 요청 모델 ---------------------
class TodoCreateRequest(BaseModel):
    title: str # 할 일의 제목 / 문자열 / 필수값
    is_done: bool = False # 할 일을 했다 안했다? -> 기본값이 False

# --- 할 일 수정 요청 모델 ----------------------
# 두 필드 모두 Optional인 이유 --> PATCH는 "부분 수정 허용"(부분 수정이 원칙)
# --> title만 내보내거나, is_done만 보내는 것도 허용해야 하기 때문이다
class TodoUpdateRequest(BaseModel):
    title: str | None = None
    is_done: bool | None = None

# --- 회원가입 요청 모델 --------------------------
class UserSignUpRequest(BaseModel):
    # Field(...) --> ...은 "필수"라는 뜻의 파이썬 뭄법(Ellips)
    # email 같은 경우는 description을 같이 쓰려면 Field() 형태가 필요하다.
    #   --> description: 코드실행에는 영향ㅣ 없고, / docs 화면에만 표시되는 문서용 문자열
    email: EmailStr = Field(..., description="사용자 이메일 주소")
    password: str = Field(..., min_length=8, description="사용자 비밀번호(평문 입력)")

    # field_validator: Pydantic 기본 검증(min_length를 8글짜 까지) 통과 후 추가로 실행되는 커스텀 규칙 (데코레이터) 
    @field_validator("password")
    def validate_password(cls, value): # cls는 클래스자기 자신, value는 매개변수(입력값)
        if not re.search(r"[A-Z]", value):
            raise ValueError("비밀번호에는 대문자가 최소 1개 포함되어야 합니다.")
        if not re.search(r"[a-z]", value):
            raise ValueError("비밀번호에는 소문자가 최소 1개 포함되어야 합니다.")
        if not re.search(r"[0-9]", value):
            raise ValueError("비밀번호에는 숫자가 최소 1개 포함되어야 합니다.")
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', value):
            raise ValueError("비밀번호에는 특수문자가 최소 1개 포함되어야 합니다.")
        return value

# --- 로그인 요청 모델 -----------------------------
class UserLoginRequest(BaseModel):
    # 회원가입과 로그인을 분리한 이유: 로그인에는 회원가입 때의 복잡한 비밀번호 규칙 검증이
    # 필요가 없다. 로그인 "이미 만들어진 비밀번호가 맞는지"만 확인하면 된다.
    email: EmailStr = Field(..., description="사용자 이메일 주소")
    password: str = Field(..., min_length=8, description="사용자 비밀번호(평문 입력)")

# --- Accescc Token 재발급 요청 모델
# 로그인 때 받은 refresh_token을 그대로 같이 보내는 용도, 필드는 하나
class RefreshTokenRequest(BaseModel):
     refresh_token: str = Field(..., description="로그인 시 발급받은 refresh token")