'''
======================================================================
repositories/user_service.py

회원가입/로그인/토큰재발급/로그아웃의 업무 규칙을담당하는 계층

======================================================================
'''
from fastapi import HTTPException,status
from models import User
from repositories.user_repository import UserRepository
from schema.request import UserSignUpRequest, UserLoginRequset
from auth.password import hash_password, verify_password
from auth.jwt import create_access_token, create_refresh_token,decode_token

class UserService:
    def __init__(self, repository: UserRepository):
        self.repository = repository

    def signup(self, body: UserSignUpRequest) -> User:
        """회원 가입"""
        if self.repository.find_by_email(body.email):
            # 이메일 중복 확인 -> 이미 존재하면 409(Conflict)로 거부한다.
            raise HTTPException(status.HTTP_409_CONFLICT, detail='이미 사용중인 이메일입니다.')
        # 비밀번호는 반드시 해싱해서 저장(평문 저장 금지)
        user = User(email=str(body.email), hashed_password=hash_password(body.password))
        return self.repository.save(user) # DB에 저장

    def login(self, body: UserLoginRequset) -> dict:
        """로그인"""
        user = self.repository.find_by_email(body.email)
        if not user or not verify_password(body.password, user.hashed_password):
            # 이메일이 없는 경우와 비밀번호가 틀ㄹ니 경우를 같은 에러 메시지로 묶는다.
            # --> 따로 알려주게 되면 공격자가 예측할 수 있다. 이메일이 가입되어 있는 상태인지 등
            # 추측할 수 있기 때문에 보안상 두 경우를 구분하지 않는다.
            raise HTTPException(
                status.HTTP_401_UNAUTHORIZED,
                detail='이메일 또는 비밀번호가 올바르지 않습니다.'
            )
        
        access_token = create_access_token(user_id=user.id)
        refresh_token = create_refresh_token(user_id=user.id)

        # refresh_token을 DB에 저장한다. --> 로그아웃이 가능하다.
        user.refresh_token = refresh_token
        self.repository.save(user)

        return{'access_token': access_token, 'refresh_token': refresh_token}
    
    def refresh(self, refresh_token: str) -> dict:
        """
        access token이 만료됐을 때, 재로그인 없이 새 access token만 발급받는 기능
        1번째 검증: decode_token(..., expected_type='refresh') -> 서명이 유효하고, 만료되지 않은,
        'refresh'타입이 맞는지 확인 (access token을 넣으면 거부된다.)
        2번째 검증: DB에 저장된 값과 일치하는지 확인 -> 로그아웃을 했거나 이미 폐기된 토큰이면,
                   서명 자체는 통과되어도 DB에 없으니 거부된다
        """
        user_id = decode_token(refresh_token, expected_type='refresh')
        user = self.repository.find_by_id(user_id)

        if not user or user.refresh_token != refresh_token:
            raise HTTPException(
                status.HTTP_401_UNAUTHORIZED,
                detail='유효하지 않은 refresh token 입니다. 다시 로그인 해주세요'
            )
        
        return {'access_token': create_access_token(user_id=user.id)} # 새 access token 발급

    def logout(self, refresh_token: str) -> None:
        """
        DB에 저장해둔 refresh_token을 지워서 "로그아웃"을 구현
        (쿠키/세션 방식이 아니라 DB기반이라는 것이 핵심이다.
        JWT는 stateless, 서버가 스스로 토큰을 무효화한다는 개념이 원래는 없다.
        refresh_token 만큼은 DB로 추적해서 로그아웃을 실제로 동작하게 만든다.
        access_token 자체는 만료 전까지는 여전히 유효하다는 점이 한계다.)
        """
        user_id = decode_token(refresh_token, expected_type='refresh')
        user = self.repository.find_by_id(user_id)
        if user:
            user.refresh_token = None # None으로 초기화(로그아웃)
            self.repository.save(user) # 로그아웃한 것을 저장