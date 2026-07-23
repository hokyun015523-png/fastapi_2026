# ==================================================================================
# football/test_main.py
#
# pytest로 단위테스트 /  pytest test_main.py 실행 할때 코드
#    test_crud.py : crud.py 함수를 직접 호출해서 DB 조회 로직만 검증
#    test_main.py : 실제 HTTP 요청(GET)을 흉내내서, main.py에 정의된 엔드포인트가
#                 올바른 url / 상태코드 / 응답 구조로 동작하는지 검증
#                 이 파일이 통과해야 'API로서 완성됐다'라고 결정

# TestClient 
#   uvicorn 서버를 실제로 띄우지 않고도 FastAPI 앱을 호출할 수 있게 해준다.
#   main.py의 app 객체를 파이썬 함수 호출 수준에서 직접 실행해주기 때문에 
#   네크워크 소켓을 열지 않고도 훨씬 빠르게 같은 결과를 확인할 수 있다.
#
# 왜 이 도구들을 사용하는가?
#   1) Swagger UI에서 하나하나 클릭하고, 응답 결과를 눈으로 읽고, 숫자를 세는 행위는 
#      느리고, 지치고, 실수가 생실 수 있다. 이 확인 과정ㅇ르 "코드로 자동화" 했다.
#   2) 회귀(regression)방지
#      오늘 만든 기능이 내일 다른 코드 수정 때문에 망가지는 것을 자동으로 잡아내기 위해
#       pytest 한 줄 치면 수십개 테스트가 몇 초만에 실행된다. --> 증거로 확인
#   3) TestClient를 사용하는 이유는 "서버를 안켜도 되니까"
#      진짜 서버(uvicorn)를 켜려면 포트를 열고, 네트워크 소켓을 열고, 실제로 통신을
#      해야 한다. --> 느리고, 포트 충돌 같은 부수적인 문제도 생긴다.
#      TestClient는 ㅛ실제 네트워크 통신 없이 main.py의 app 객체를 파이썬 함수 호출
#      수준에서 그대로 실행 --> 서버를 따로 켜둘 필요가 없다.
#      --> pytest 한 줄로 API 테스트가 가능하다.
# ==================================================================================
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_read_main():
    """루트 헬스 체크 엔드포인트가 정상 메시지를 반환하는지 확인"""
    response = client.get('/')

    assert response.status_code == 200 # 요청이 성공했다

    # .json()를 호출하면 응답 본문 문자열을 파이썬 딕셔너리로 파싱해준다. 
    # (requests 라이브러리의 response와 같은 방식)
    assert response.json() == {'message': 'API 상태 확인 성공'}

def test_read_players():
    """
    선수 목록 조회 엔드포인트가 데이터 전체를 반환하는지 확인

    limit=10000 처럼 실제 선수 수(1018명)보다 훨씬 큰 값을 줘서 페이지네이션 때문에
    일부만 잘리지 않고, 전체가 다 오는지 확인한다.
    
    """
    response = client.get('/v0/players/?skip=0&limit=10000')

    assert response.status_code == 200

    assert len(response.json()) == 1018

def test_read_players_by_name():
    """이름/성 쿼리 파라미터 필터가 문서와 같은 방식으로 동작하는지 확인"""
    response = client.get('/v0/players/?first_name=Bryce&last_name=Young')

    # assert : 합격/ 불합격을 판정하는 채점 기준이라고 생각
    #          조건이 참이 아니면 여기서 즉시 실패로 멈춤
    #          성공하면 그냥 넘어간다. 실패시 에러로 알린다.
    assert response. status_code == 200
    assert len(response.json()) == 1 # 1명만 나와야
    assert response.json()[0].get('player_id') == 2009

def test_read_players_with_id():
    """경로 파라미터 player_id로 선수 1명을 조회할 수 있는지 확인"""
    response = client.get('/v0/players/1001')

    assert response.status_code == 200
    assert response.json().get('player_id') == 1001

def test_read_performances():
    """"성적 목록 조회 엔드포인트가 전체 성적 데이터를 반환하는지 확인"""
    response = client.get('/v0/performances/?skip=0&limit=20000') 

    assert response.status_code == 200
    assert len(response.json()) == 17306

def test_read_performances_by_date():
    """minimum_last_changed_date 쿼리 파라미터로 증분 조회가 되는지 확인"""
    response = client.get(
        '/v0/performances/?skip=0&limit=20000&minimum_last_changed_date=2024-04-01'
    )
    assert response.status_code == 200
    # 2024-04-01 이후 변경 데이터만 남는지 확인 
    assert len(response.json()) == 2711

def test_read_leagues_with_id():
    """리그 상세 조회에서 teams relationship이 응답에 포함되는지 확인"""
    response = client.get('/v0/league/5002/')

    assert response.status_code == 200

    # response.json()['teams']
    # schemas.League.teams: List[TeamBase] 필드와 같다.
    # JSON의 "teams" 배열로 직렬화 되었다.
    assert len(response.json()['teams']) == 8 

def test_read_leagues():
    """리그 목록 조회 엔드포인트의 기본 응답 개수 확인"""
    response = client.get('/v0/leagues/?skip=0&limit=500')

    assert response.status_code == 200
    assert len(response.json()) == 5

def test_read_teams():
    """팀 목록 조회 엔드포인트의 전체 팀 데이터를 반환하는지 확인"""
    response = client.get('/v0/teams/?skip=0&limit=500')

    assert response.status_code == 200
    assert len(response.json()) == 20

def test_read_teams_for_one_league():
    """league_id 쿼리 파라미터로 특정 리그의 팀만 조회되는지 확인"""
    # 전체 20개의 팀중 league_id=5001 소속인 12개만 응답에 남아야 한다.
    response = client.get('/v0/teams/?skip=0&limit=500&league_id=5001')

    assert response.status_code == 200
    assert len(response.json()) == 12

def test_counts():
    """분석용 counts 엔드포인트가 리그/팀/선수 수를 정확히 반환하는지 확인"""
    response = client.get('/v0/counts/')
    response_data = response.json()

    assert response.status_code == 200

    assert response_data['league_count'] == 5
    assert response_data['team_count'] == 20
    assert response_data['player_count'] == 1018