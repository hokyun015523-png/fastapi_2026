#===============================================================
# 09_NCS-drug/database.py
# 
# DB 연결(Engine) 생성과 여러 모듈에서 
# 공통으로 사용하는 DB 유틸리티 함수를 정의
# 
#===============================================================
from sqlalchemy import create_engine, text

from config import DB_URL, SOURCE_TABLE

#===============================================================
# DB Enging 생성
#===============================================================
engine = create_engine(DB_URL, echo=False)

def table_count(table_name: str) -> int:
    """지정한 테이블의 전체 데이터 개수를 반환한다."""

    with engine.connect() as conn:
        return conn.execute(text(f'SELECT COUNT(*) FROM {table_name}')).scalar_one()

def check_required_tables() -> None:
    """
    배치처리와 이벤트 처리를 수행하기 전에 
    원본 테이블이 존재하는지 확인한다.
    """

    checks = [
        (SOURCE_TABLE, "의약품 연령금기 데이터가 먼저 적재되어야 합니다.")
    ]
    for table_name, hint in checks:
        try:
            count = table_count(table_name)
        except Exception as exc:
            raise RuntimeError(f'{table_name} 테이블을 확인할 수 없습니다. {hint} 원인: {exc}') from exc
        if count ==0:
            raise RuntimeError(f'{table_name} 테이블이 존재하지만 데이터가 없습니다. 저장시스템 적제를 먼저 확인하세요')

def execute_sql(sql: str, params: dict | None = None) -> None:
    """여러 문장으로 이루어진 SQL문을 순서대로 실행한다."""

    with engine.begin() as conn:
        statements = [statement.strip() for statement in sql.split(';') if statement.strip()]
        for statement in statements:
            conn.execute(text(statement), params or {})

# def table_count(table_name: str) -> int:

#     with engine.connect() as conn:

#         return conn.execute(
#             text(f'SELECT COUNT(*) FROM {table_name}')
#         ).scalar_one()