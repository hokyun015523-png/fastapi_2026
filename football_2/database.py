# =============================================================================
# football/database.py 
#
#   - SQLAlchemy 2.0 버전으로 코드 변경
#   - PostgreSQL 데이터베이스와 연결
#   - 다른 파일들 (models.py, crud.py, main.py)에서 공통으로 가져다 사용할 
#       engine / SessionLocal / Base 세 가지를 만들어 둔다.
# =============================================================================
import os

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

# ------------------------------------------------------------------------------------
# DeclarativeBase: SQLAlchemy 2.0에서 새로 생긴 "모델의 공통 조상 클래스"를 만드는 방식
#                  지난 시간 쓰던 declarative_base() 함수 호출 방식 대신, 
#                     진짜 파이썬 클래스를 상속하는 방식으로 변경되었다.

# sessionmaker: "세션 공장"을 만들어주는 함수
#                 이 공장에서 세션을 하나씩 찍어내서 (SesstionLocal()) DB와 대화한다.

# os.getenv('DATABASE_URL', 기본값): 환경변수 DATABASE_URL이 설정되어 있으면
#                                 그 값을 사용하고, 없으면 두 번째 인자(기본값)을 사용
# ------------------------------------------------------------------------------------

SQLALCHEMY_DATABASE_URL = os.getenv(
    'DATABASE_URL',
    'postgresql://postgres:1234@localhost:5432/swc_api'
)

# ------------------------------------------------------------------------------------
# create_engine: engine은 DB와 실제로 통신하는 "커넥션 풀"을 관리하는 객체.
#             매번 새로 연결을 맺지 않고, 미리 만들어둔 연결 여러 개를 재사용한다.

# pool_pre_ping=True
#     - 풀에서 연결을 꺼내 쓰기 전에 "SELECT 1" 같은 가벼운 쿼리를 먼저 날려서
#       그 연결이 아직 살아있는지 확인한다. 
#       PostgreSQL 서버 재시작, 오랜 유휴 상태로 인한 연결 끊김 등으로 "죽은 연결"을
#       그대로 재사용하려다가 에러가 나는 상황을 막아준다.
# ------------------------------------------------------------------------------------
engine = create_engine(SQLALCHEMY_DATABASE_URL, pool_pre_ping=True)

# ------------------------------------------------------------------------------------
# SessionLocal - 세션 공장
#     2.0 버전에서는 autocommit 모드를 사용하지 않는다.
#     항상 session.commit() / session.rollback() 으로 트랜잭션 경계를 개발자가 직접,
#     명시적으로 정한다.
# ------------------------------------------------------------------------------------
SessionLocal = sessionmaker(bind=engine, autoflush=False)

class Base(DeclarativeBase):
    """모든 ORM 모델들이 상속하는 SQLAlchempy 2.0의 선언적 기준 클래스"""
    pass