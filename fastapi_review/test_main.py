#==================================================================================
# fastapi_review/test_main.py
#   2026-06-30
#   
#   pytest 라이브러리 --> python 표준 테스트 도구
#       파일 이름이 test_로 시작해야 한다.
#       함수 이름이 test_로 시작해야 한다.
#       권장사항> 테스트DB도 따로 만들어준다. 
#       uv add pytest --> 설치를 해준다.
#   
#==================================================================================

# 1. 라이브러리 불러오기
import pytest
from fastapi.testclient import TestClient # 서버 없이 FastAPI에 요청하는 가짜 클라이언트
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from main import app  # 테스트할 FastAPI 앱
from database import Base  # 테이블 생성/삭제에 사용
from dependencies import get_db   # 테스트용 DB로 교체할 원본 get_db

# 2. 테스트 전용 DB를 설정
TEST_DATABASE_URL = 'postgresql+psycopg2://postgres:1234@localhost:5432/reviewdb_test'

# 테스트용 엔진 --> reviewdb_test에 접속
test_engine = create_engine(TEST_DATABASE_URL)

# 테스트용 세션 팩토리 --> database.py의 SessionLocal과 동일한 구조, DB만 다름
TestingSessionLocal = sessionmaker(
    autocommit=False,  # 직접 커밋 호출해야 저장
    autoflush=False, # 커밋 전 자동 반영 안 한다.
    bind=test_engine  # 테스트용 엔진에 연결
)

# 3. fixture(미리 준비한다, 테스트 함수가 실행되기 전에 미리 준비): 테이블 생성/삭제
# pytest가 자동으로 호출해준다. 
# scope='module' --> 이 파일 전체에서 딱 한 번만 실행된다. 
@pytest.fixture(scope='module') 
def setup_db():
    """이 파일의 모든 테스트가 시작되기 전 딱 한 번 실행
    yield 위 : 테스트 전 준비 (테이블 생성) --> reviewdb_test에 테이블 생성
                Base를 상속한 모든 모델(User, Item)의 테이블이 생성된다.
    yield 아래 : 테스트 후 정리 (테이블 삭제)
                다음에 pytest 실행 시 깨끗한 상태로 시작하기 위해 
    
    """
    Base.metadata.create_all(bind=test_engine)
    print('\n[setup] 테스트 테이블 생성 완료!')

    yield  # 이 시점에 다른 테스트 함수들이 순서대로 실행된다.

    Base.metadata.drop_all(bind=test_engine)
    # teardown : 테스트가 끝난 뒤 정리(총소)하는 작업
    print('\n[teardown] 테스트 테이블 삭제 완료!')

# 4. fixture: TestClient 준비
@pytest.fixture(scope='module')
def client(setup_db):
    """get_db를 테스트용으로 교제하고 TestClient를 생성"""
    # 테스트용 get_db: reviewdb_test에 연결하는 버전
    def override_get_db():
        db = TestingSessionLocal() # reviewdb_test 세션 생성
        try:
            yield db
        finally:
            db.close()  # 세션 닫기

    # 원본 get_db를 테스트용으로 교체 --> FastAPI가 get_db를 호출하면 override_get_db가 실행
    app.dependency_overrides[get_db] = override_get_db

    # with 구문: TestClient 생성 및 정리를 자동 관리
    # TestClinet(app): 실제 서버 없이 app에 직접 HTTP 요청 가능
    with TestClient(app) as c:
        yield c  # 테스트 함수에서 client라는 이름으로 이 c를 받아 사용

    # with 종료 후: dependency_overrides 초기화 --> 다른 테스트 파일에 영향 주지 않도록 원상복귀
    app.dependency_overrides.clear()

# 5. 테스트 함수들
def test_create_user(client):
    """유저 생성 -> 200 응답, 이메일 일치, 비밀번호 미노출, items 빈 리스트 확인 """
    response = client.post(
        '/users/',
        json={
            'email': 'test@example.com',
            'password': 'secret123'
        }
    )

    # HTTP 상태코드 200(성공) 확인
    # assert --> "이 값이 맞는지 확인해라" Python 내장 명령어
    assert response.status_code == 200, f'예상: 200, 실제: {response.status_code}'

    data = response.json() # 응답 바디를 딕셔너리로 변환해서 저장

    # 응답 내용 확인
    assert data['email'] == 'test@example.com' # 입력한 이메일이 그대로 반환되는지
    assert data['is_active'] == True   # 기본값 True 확인

    # 보안 확인: 비밀번호가 어떤 형태로도 응답에 포함되지 않아야 한다.
    assert 'password' not in data   # 평문 비밀번호 없음
    assert 'hashed_password' not in data  # 해시된 비밀번호도 없음

    # 처음 생성 시 아이템이 없으므로 빈 리스트
    assert data['items'] == []

def test_create_user_duplicate_email(client):
    """같은 이메일로 재가입 시도 -> 400 에러 + 에러 메시지 확인"""
    response = client.post(
        '/users/',
        json={
            'email': 'test@example.com', # 위 테스트에서 이미 사용한 이메일
            'password': 'different_pass'
        }
    )

    # 이 테스트는 400이 나와야 PASSED -> "실패해야 통과하는" 케이스
    assert response.status_code == 400

    assert '이미 등록된 이메일' in response.json()['detail']

def test_read_users(client):
    """유저 전체 목록 조회 -> 200 응답, 리스트 타입, 1명 이상 확인"""
    response = client.get('/users/')

    assert response.status_code == 200

    data = response.json()

    # isinstance(값, 타입) --> 값이 해당 타입인지 확인
    assert isinstance(data, list)

    # test_create_user에서 1명을 만들었으므로 최소 1명이상
    assert len(data) >= 1

def test_read_user(client):
    """1번 유저 조회 -> 200응답, id와 이메일 일치 확인"""
    response = client.get('/users/1')

    assert response.status_code == 200

    data = response.json()
    assert data['id'] == 1                        # id가 1인지
    assert data['email'] == 'test@example.com'    # 1번의 이메일이 맞는지

def test_read_users_not_found(client):
    """존재하지 않는 유저 조회 -> 404 에러 확인"""
    response = client.get('/users/9999')

    assert response.status_code == 404

def test_create_item_for_user(client):
    """1번 유저의 아이템 생성 -> 200응답 , title일치, owner_id 자동설정 확인"""
    response = client.post(
        '/users/1/items/', # 1번 유저의 아이템 생성 엔드포인트
        json={ # owner_id 는 보내지 않는다 -> 서버가 자동으로 URL 설정
            'title': '복습 아이템',
            'description': 'FastAPI 복습 중'
        }
    )

    assert response.status_code == 200

    data = response.json()
    assert data['title'] == '복습 아이템'

    # owner_id가 1로 서버에서 자동 주입되어있는지 확인
    assert data['owner_id'] == 1

def test_user_has_items(client):
    """유저 조회 시 items배열에 아이템이 포함되어있는지 확인 (1:N 관계 검증)"""
    response = client.get('/users/1')

    assert response.status_code == 200

    data = response.json()

    # 위에서 아이템 1개를 생성 -> items 가 비어있지 않아야 한다.
    assert len(data['items']) >= 1

    # 첫번째 아이템의 title이 맞는지 확인
    assert data['items'][0]['title'] == '복습 아이템'

def test_read_items(client):
    """전체 아이템 목록 조회 -> 200응답, 리스트 타입, 1개이상 확인"""
    response = client.get('/items/')

    assert response.status_code == 200

    data = response.json()
    assert isinstance(data, list) # 응답이 리스트인지 확인
    assert len(data) >= 1
