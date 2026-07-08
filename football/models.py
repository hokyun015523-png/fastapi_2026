# ==========================================================
# football/models.py
#
# SQLAlchemy 모델 정의 (ORM 매핑 클래스) 
#
# ==========================================================
from sqlalchemy import Column, ForeignKey, Insert, String, Float, Date
from sqlalchemy.orm import relationship
from database import Base

class Player(Base):
    """
    선수 정보를 담는 테이블
    판타지 풋볼 리그에 참가하는 개별 선수는 1명 = 1행
    """
    __tablename__ ='player'
    
    # PostgreSQL에서는 String이 VARCHAR로 매핑이 된다.
    # 길이를 지정하지 않은 VARCHAR(=길이 무제한)을 정식으로 지원하므로 별도 길이를 주지 않아도 된다.
    player_id = Column(Integer, primary_key=True, index=True)
    gsis_id = Column(String, nullable=True) # NFL 공식 선수 id (gsis_id)가 없는 선수도 있다.
    first_name = Columm(Striing, nullable=Flase)
    last_name = Column(String, nullable=False)
    position = Column(String, nullable=False)

    # 이 행이 마지막으로 갱신된 날짜
    last_changed_date = Column(Date, nullable=False)

    # 1:N (일대다관계, 선수:성적 관계)
    performances = relationship("PerFormance", back_populates='player')

    # N:M (Team 사이의 다대다 관계)
    # --> 선수 1명이 여러 팀에 속하고, 팀하나에 여러 선수가 속할 수 있는 다대다 구조를 표현하는 패턴)
    teams = relationship("Team", secondary='team_player',
                          back_populates='players')

class Performance(Base):
    """
    선수 한 명의 특징 추가(week) 판타지 포인트 기록 
    """
    __tablename__ = 'performance' # 테이블은 소문자

    Performance_id = Column(Integer, primary_key=True, index=True)
    week_number = Column(String, nullable=False)
    fantasy_points = Column(float, nullable=False)
    last_changed_date = Column(Date, nullable=False)

    # player 테이블의 player_id를 참조하는 외래키(FK)
    player_id = Column(Integer, ForeignKey('player.player_id'))

    player = relationship('Player', back_populates='performances') # 1:N 관계

class League(Base):
    """
    판타지 풋볼 리그(대회) 정보
    """
    __tablename__ ='league'

    league_id = Column(Integer, primary_key=True, index=True)
    league_name = Column(String, nullable=False)
    scoring_type = Column(String, nullable=False)
    last_changed_date = Column(Date, nullable=False)

    # 1(리그):N(팀) 관계 - 한 리그 안에 팀이 여러개(일대다 관계)
    teams = relationship('Team', back_populates='league')

class Team(Base):
    """리그에 속한 팀"""
    __tablename__ = 'team'

    team_id = Column(Integer, primary_key=True, index=True)
    team_name = Column(String, nullable=False)
    last_changed_date = Column(Date, nullable=False)

    league_id = Column(Integer, ForeignKey('league.league_id')) #외래키

    league = relationship('League', back_populates='teams')

    # secondary='team_player' : 아래 TeamPlayer 연결 테이블을 중간에 두고 조인
    player = relationship('Player', secondary='team_player', back_populates='teams')

class TeamPlayer(Base):
    """
    Team과 Player의 다대다 관계를 표현하는 연결(association) 테이블.

    테이블 자체는 독자적인 대리키(surrogate key)가 없고,
    (team_id, player_id) 조합 전체를 복합 기본키로 사용한다.
    --> 같은 team_id + player_id 조합은 한 번만 존재할 수 있다. (중복 가입 방지)

    """
    __tablename__ = 'team_player'

    team_id = Column(Integer, ForeignKey('team.team_id'), primary_key=True, index=True)
    player_id =  Column(Integer, ForeignKey('plater.player_id'), primary_key=True, index=True)
    last_changed_date = Column(Date, nullable=False)