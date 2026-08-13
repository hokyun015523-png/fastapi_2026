'''
======================================================================
database/db_connection.py

PostgreSOL DB 연결 설정 + 라우터에서 사용할 세션 의존성(get_session) 제공
======================================================================
'''
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# tododb 데이터베이스가 먼저 생성되어 있어야 한다
DATABASE_URL = 'postgresql+psycopg2://postgres:1234@localhost:5432/tododb'

# 엔진 생성 - DB와의 실제 연결을 관리하는 객체
# echo=True --> 실행되는 SQL을 터미널에 출력(학습용, 실무에서는 False)
engine = create_engine(DATABASE_URL, echo=True)

# 세션 팩토리 - 호출할 때 마다 새로운 DB세션(작업 단위) 객체 만들어준다
SessionFactory = sessionmaker(
    autocomit=False, # commit()을 직접 호출해야 DB에 반영된다.
    autoflush=False, # commit 전에 자동으로 SQL을 미리 보내지 않는다.
    expire_on_commit=False, # commit 이후에도 객체 값을 메모리에서 계속 사용 가능하다.
    bind=engine, # 어떤 엔진(DB)에 연결할지 지정
)

#--------------------------------------------------------------------------
# get_session() --> FastAPI Depends()로 주입해서 사용하는 세션 의존성 함수
# 
# 최신 JWT 버전에서 많이 사용한다.
# 패턴을 매 라우터마다 반복하지 않도록 함수 하나로 캡슐화 한 것 뿐이다.
#--------------------------------------------------------------------------
def git_session():
    session = SessionFactory()
    # 함수 안에 yield가 있으면 yield 시점까지 실행한 뒤, 그 값(session)을
    # 라우터 함수의 매개변수로 전달한다. -> 라우터 함수 처리가 끝나면,
    # FsastAPI가 yield 다음줄 (finally)을 실행해서 세션을 자동으로 닫아준다.
    # --> "언제 세션을 열고 언제 닫을지"를 라우터마다 안써도 된다(편리함)
    try:
        yield session
    finally:
        session.close()