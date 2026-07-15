# =========================================================================
# football/crud.py
#    - SQLAlchemy 2.0 버전으로 코드 변경

# 데이터 쿼리를 수행하는 도우미 함수 (헬퍼 함수)
#   생성, 조회, 수정, 삭제의 약어 CRUD

# select() 문장을 먼저 "설계"하고, db.scalars(stmt)로 "실행"하는 조회함수
#   - select() --> 아직 실행되지 않은 SQL 
#   - db.scalars(stmt) 또는 db.execute(stmt)를 호출하는 순간 실제로 실행된다.

# from sqlalchemy import func, select
#   func --> COUNT, SUM처럼 SQL의 집계함수를 파이썬에서 사용할 때
#   select --> SELECT 문장을 설계하는 함수(아직 실행 아님) 

# from sqlalchemy.orm import Session, joinedload, selectinload
#   Session --> DB와 대화하는 작업공간
#   joinedload --> 관계 데이터를 SQL JOIN으로 한 번에 같이 가져오는 옵션
#   selectinload --> 관계 데이터를 "추가 SELECT 한 번"으로 따로 가져오는 옵션
# =========================================================================
from sqlalchemy import func, select
from sqlalchemy.orm import Session, joinedload, selectinload

from datetime import date

import models

def get_player(db: Session, player_id: int):
    """
    기본키로 선수 한 명을 조회한다.
    
    db.get(모델클래스, 기본키값) --> 기본키로 딱 한 건만 조회할 때 사용하는 전용 메서드
    """
    return db.get(models.Player, player_id)

def get_players(db: Session, skip: int = 0, limit: int = 100,
                min_last_changed_date: date | None = None,
                last_name: str | None = None,
                first_name: str | None = None):
    """선수 목록에 선택 조건을 추가하고 페이지 단위로 조회한다."""
    stmt = select(models.Player) # SQL 설계

    if min_last_changed_date:
        stmt = stmt.where(models.Player.last_changed_date >= min_last_changed_date)
    if first_name:
        stmt = stmt.where(models.Player.first_name == first_name)
    if last_name:
        stmt = stmt.where(models.Player.last_name == last_name)

    stmt = stmt.offset(skip).limit(limit) # 페이지네이션

    # .scalars() --> 각 행에서 첫번째 컬럼(여기서는 Player객체자체)만 꺼내서
    #                   리스트처럼 다루게 해주는 결과 객체 반환
    # .all() --> 그 결과를 실제 파이썬 리스트로 변환해서 반환
    return db.scalars(stmt).all()  # SQL 실행

def get_performances(db: Session, skip: int = 0, limit: int = 100,
                     min_last_changed_date: date | None = None):
    """경기 성적(Performance) 레코드 목록을 조회한다. get_players와 동일한 패턴""" 
    stmt = select(models.Performance)
    if min_last_changed_date:
        stmt = stmt.where(models.Performance.last_changed_date >= min_last_changed_date)
    stmt = stmt.offset(skip).limit(limit) # 페이지네이션
    return db.scalars(stmt).all()

def get_league(db: Session, league_id: int | None = None):
    """
    리그 하나를 league_id로 조회한다.

    league_id가 None으로 들어온 경우 db.get(모델, None)을 그대로 호출하면
    의도치 않은 에러가 발생할 가능성이 높다. 미리 None을 걸러낸다.
    """
    if league_id is None:
        return None
    return db.get(models.League, league_id)

def get_leagues(db: Session, skip: int = 0, limit: int = 100, 
                min_last_changed_date: date | None = None,
                league_name: str | None = None):
    """
    리그 목록을 조회, 각 리그에 속한 teams까지 한 번에 즉시 로딩(eager load)

    joinedload --> SQL JOIN으로 리그와 팀을 "한 번의 쿼리"로 같이 가져온다
    (Lazy loading --> N+1 문제 해결)
    
    """
    stmt = select(models.League).options(joinedload(models.League.teams))
    if min_last_changed_date:
        stmt = stmt.where(models.League.last_changed_date >= min_last_changed_date)
    if league_name:
        stmt = stmt.where(models.League.league_name == league_name)
    stmt = stmt.offset(skip).limit(limit)

    # .unique() --> 중복된 리그 행을 하나로 합쳐라.
    return db.scalars(stmt).unique().all()