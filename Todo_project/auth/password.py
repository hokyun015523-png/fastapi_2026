'''
======================================================================
auth/password.py

비밀번호를 해싱(암호화 저장) / 검증을 담당하는 모듈

pwdlib 라이브러리 사용 -> 장점: 내부적으로 salt(무작위 값)을 자동으로 섞어서 해싱하기 때문에
                         같은 비밀번호를 넣어도 배번 다른 해싱값이 생성된다.
                         공격자(해커)가 미리 계산해둔 해시 목록으로 대조하는 공격을 막을 수 있다.
                         FastAPI에서 권장하는 최신 보안 라이브러리
======================================================================
'''
from pwdlib import PasswordHash

# PasswordHash.recommended() : pwdlib라이브러리가 현재 가장 안전하다고 권장하는 해시 알고리즘을 
#                              자동으로 선택해준다.
#                              (기본적으로 Argon2id - bcrypt보다 GPU 기반 무차별 대입 공격에 더 강한 최신 알고리즘)
password_hasher = PasswordHash.recommended()

def hash_password(plain_password: str) -> str:
    """평문 비밀번호 -> 해싱값으로 변환(회원가입 시 DB 저장 직전에 사용)"""
    return password_hasher.hash(plain_password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """로그인 시 사용자가 입력한 평문 비밀번호가 DB에 저장된 해시값과 일치하는지 검증
       해시는 복구화가 불가능하므로, 저장된 해시를 평문으로 되돌리는것이 아니라
       입력값을 같은 방식으로 다시 해싱해서 두 해시가 같은지를 비교한다.
       (pwdlid의 verify()함수가 대신 처리한다.)
    """
    return password_hasher.verify(plain_password, hashed_password)