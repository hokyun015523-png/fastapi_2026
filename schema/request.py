from pydantic import BaseModel, EmailStr, Field, field_validator
import re # 파이썬에서 정규표현식을 쉽게 사용할 수 있도록 도와주는 라이브러리

# 할 일 생성 요청 모델
class TodoCreateRequest(BaseModel):
    title: str
    is_done: bool = False

# 할 일 수정 요청 모델
class TodoUpdateRequest(BaseModel):
    title: str | None = None
    is_done: bool | None = None

# 회원가입 요청 모델
class UserSignUpRequest(BaseModel):
    email: EmailStr = Field(..., description='사용자 이메일 주소')
    password: str = Field(..., min_length=8, description='사용자 비밀번호(평문 입력)')

    @field_validator('password')
    def validate_password(cls, value):
        if not re.search(r'[A-Z]', value):
            raise ValueError('비밀번호에는 대문자가 최소 1개 포함되어야 합니다!')
        if not re.search(r'[a-z]', value):
            raise ValueError('비밀번호에는 소문자가 최소 1개 포함되어야 합니다!')
        if not re.search(r'[0-9]', value):
            raise ValueError('비밀번호에는 숫자가 최소 1개 포함되어야 합니다!')
        if not re.search(r'[!@#$%^&*(),.?\"{}|<>]', value):
            raise ValueError('비밀번호에는 특수문자가 최소 1개 포함되어야 합니다!')
        return value
        