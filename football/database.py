# ==========================================================
# football/batabase.py
# ==========================================================
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

DB_URL = 'postgresql://postrgres:123@localhost:5432/swc_api'

# create_engine은 DB와 통신할 커넥션 풀을 만든다.
# pool_pre_ping=True --> 풀에서 커넥션을 꺼내쓰기 전에 "SELECT 1"같은
# 가벼운 쿼리로 살아있는 연결인지 먼저 확인한다.
# PostgreSQL 서버 재시작, 유휴 연결 타임아웃, 네트워크 단절  등으로 죽어버린 연결을
# 재사용하려다 에러가 나는 상황을 막아준다.
engine = create_engine(DB_URL, pool_pre_ping=True)

# FastAPI 요청마다 새 DB 세션을 만들 때 사용할 "세션 팩토리 "
sessionLocal = sessionmaker(autoflush=False, autocommit=False, bind=engine)

Base = declarative_base()