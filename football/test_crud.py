# =====================================================
# football/test_crud.py
#
# pytest로 단위테스트
# =====================================================
import pytest
from datetime import date    

from sqlalchemy.orm import Session
from sqlalchemy.orm import joinedload
                                                                 
import models
import crud
from database import SessionLocal

# min_last_changed_date 필터 테스트를 위한 기준 날짜 (2024-04-01)
test_date = date(2024, 4, 1)

@pytest.fixture(scope='function')
def db_session():
    """
    테스트 함수마다 새 DB 세션을 열고, 테스트가 끝나면 닫는다.

    scope='function' --> 테스트 하나당 세션을 새로 만든다.
    세션을 공유하지 않기 때문에 테스트 간 서로 오염될 걱정이 적다

    """
    session = SessionLocal()
    yield session
    session.close()


def test_get_player(db_session):
    """player_id=1001인 선수를 정확히 가져오는지 확인"""
    player = crud.get_player(db_session, player_id=1001)
    assert player.player_id == 1001


def test_get_players(db_session):
    """
    2024-04-01 이후 변경된 선수 수가 seed 데이터 기준 1018명인지 확인    
    """
    players = crud.get_players(db_session, skip=0, limit=10000,
                               min_last_changed_date=test_date)
    assert len(players) == 1018


def test_get_all_performances(db_session):
    """전체 성적 기록 수가 17306건인지 확인"""
    performances = crud.get_performances(db_session, skip=0, limit=18000)
    assert len(performances) == 17306


def test_get_new_performances(db_session):
    """2024-04-01 이후 갱신된 성적 기록이 2711건인지 확인"""
    performances = crud.get_performances(db_session, skip=0, limit=10000,
                                         min_last_changed_date=test_date)
    assert len(performances) == 2711


def test_get_league(db_session):
    """
    league_id=5002 리그를 가져오고, 소속 팀이 8개인지 확인

    league.teams에 접근하는 순간
    SQLAlchemy가 지연 로딩(lazy load)으로 추가 쿼리 날려 teams를 채운다

    """
    league = crud.get_league(db_session, league_id=5002)
    assert league.league_id == 5002
    assert len(league.teams) == 8


def test_get_leagues(db_session):
    """
    전체 리그 수가 5개인지 확인
    """
    leagues = crud.get_leagues(db_session, skip=0, limit=10000,
                               min_last_changed_date=test_date)
    assert len(leagues) == 5


def test_get_teams(db_session):
    """전체 팀 수가 20개인지 확인"""
    teams = crud.get_teams(db_session, skip=0, limit=10000,
                           min_last_changed_date=test_date)
    assert len(teams) == 20


#### 내일 함수 작성 예정 ####



# 분석 쿼리 (단순 카운트) -----------------------------------------
def get_player_count(db: Session):
    """전체 선수 수를 센다."""
    query = db.query(models.Player)
    return query.count()

def get_team_count(db: Session):
    """전체 팀 수를 센다."""
    query = db.query(models.Team)
    return query.count()

def get_league_count(db: Session):
    """전체 리그 수를 센다."""
    query = db.query(models.League)
    return query.count()