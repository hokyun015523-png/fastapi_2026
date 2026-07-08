# =====================================================
# football/crud.py
#
# 데이터 쿼리를 수행하는 도우미 함수 (헬퍼 함수)
#   생성, 조회, 수정, 삭제의 약어 CRUD
# =====================================================
from sqlalchemy.orm import Session
from sqlalchemy.orm import joinedload
from datetime import date                                                                     
import models

def get_player(db: Session, player_id: int):
    """player_id 하나로 선수 1명을 조회한다. 없으면 None을 반환"""
    return db.query(models.Player).filter(
        models.Player.player_id == player_id
    ).first() # player_id의 첫번째 레코드(행)를 조회하고 반환

def get_players(db: Session, skip: int = 0, limit: int = 100, 
                min_last_changed_date: date = None,
                last_name: str = None, first_name: str = None):
    """
    선수 목록을 조건에 따라 필터링해서 가져온다.

    - skip / limit : 페이지네이션
    - min_last_changed_date : 이 날짜 "이후"에 변경된 행만 가져온다.
    - first_name / last_name : 이름으로 정확히 일치하는 선수만 가져온다.
    
    """
    query = db.query(models.Player)
    if min_last_changed_date:
        query = query.filter(
            models.Player.last_changed_date >= min_last_changed_date
        )
    if first_name:
        query = query.filter(
            models.Player.first_name == first_name
        )
    if last_name:
        query = query.filter(
            models.Player.last_name == last_name
        )
    return query.offset(skip).limit(limit).all()

def get_performances(db: Session, skip: int = 0, limit: int = 100,
                     min_last_changed_date: date = None):
    """경기 성적(Performance) 레코드 목록을 조회한다. get_players와 동일한 패턴"""
    query = db.query(models.Performance)
    if min_last_changed_date:
        query = query.filter(
            models.Performance.last_changed_date >= min_last_changed_date
        )
    return query.offset(skip).limit(limit).all()

def get_league(db: Session, league_id: int = None):
    """리그 하나를 league_id로 조회한다"""
    return db.query(models.League).filter(
        models.League.league_id == league_id
    ).first()

def get_leagues(db: Session, skip: int = 0, limit: int = 100,
                min_last_changed_date: date = None, league_name: str = None):
    """
    리그 목록을 조회, 각 리그에 속한 teams까지 한 번에 즉시 로딩(eager load)
    joinedload(models.League.teams)를 사용하면 League를 조회할 때 
    SQL JOIN으로 Team까지 한 번의 쿼리로 같이 가져온다.

    """
    query = db.query(models.League).options(joinedload(models.League.teams))
    if min_last_changed_date:
        query = query.filter(
            models.League.last_changed_date >= min_last_changed_date
        )
    if league_name:
        query = query.filter(models.League.league_name == league_name)
    return query.offset(skip).limit(limit).all()

def get_teams(db: Session, skip: int = 0, limit: int = 100,
              min_last_changed_date: date = None, 
              team_name: str = None, league_id: int = None):
    """팀 목록을 조회한다. league_id를 주면 특정 리스 소속 팀만 필터링한다."""
    query = db.query(models.Team)
    if min_last_changed_date:
        query = query.filter(
            models.Team.last_changed_date >= min_last_changed_date
        )
    if league_id:
        query = query.filter(models.Team.league_id == league_id)
    return query.offset(skip).limit(limit).all()

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