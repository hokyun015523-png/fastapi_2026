# ==============================================================================
# auth/password.property
# - 비밀번호 해상(암호화 저장) / 검증을 담당하는 모듈
# - pwdlib 라이브러리 사용
# - 내부적으로 무작위값을 자동을 섞어서 해싱하기 때문에  같은 비밀번호라도
# - 매번 다른 해싱 값이 생성이 된다.(argon2 알고리즘)

# 해싱(hashing)
# - 입력값을 일방향(one-way) 알고리즘을 통해 완전히 다른 문자열로 변환하는 과정
# - 이렇게 생성도니 결과값을 해시(hash)라고 한다.
# - 변환된 값을 다시 원래 값으로 되돌릴 수 없다.
# - 해시값만 가지고 원래의 입력값으로 역으로 계산하는 것은 불가능하다.
# - 인증은 원본 비밀번호가 아닌 해시값을 기준으로 이루어진다.
# - FastAPI 공식 문서에서 argon2 비밀번호 해싱 알고리즘을 권장
#        -> GPU 병렬 연산이나 메모리 기반 공격 등 최신 공격 기법을 고려해 설계된 현대적인 알고리즘
#        -> 현재 비밀번호 해싱 분야에서 가장 안전한 선택지로 평가받고 있다.
#   uv add pwdlib[argon2]
# ==============================================================================
from pwdlib import PasswordHash

# pwdlib가 현재시점에서 가장 안전하다고 권장하는 해시 알고리즘 조합을 자동으로 선택해준다.
password_hasher = PasswordHash.recommended()

def hash_password(plain_password: str) -> str:
    """평문 비밀번호 -> 해시값으로 변환(회원가입시 DB에 저장하기 전에 사용)"""
    return password_hasher.hash(plain_password)
def verify_password(plain_password: str, hashed_password: str) -> bool:
    """로그인 시, 사용자가 입력한 평문 비밀번호가 DB에 저장된 해시값과 일치하는지 검증"""
    return password_hasher.verify(plain_password,hashed_password)