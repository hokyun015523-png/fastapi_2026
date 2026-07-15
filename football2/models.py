# ==========================================================================
# football/models.py
#    - SQLAlchemy 2.0 버전으로 코드 변경
#       
# SQLAlchemy 모델 정의 (ORM 매핑 클래스)
#   - DB 테이블 5개 (player, performance, league, team, team_player)fmf
#     파이썬 클래스로 표현하는 "ORM 모델 정의" 파일이다.
#
#   - Mapped[...] --> 이 속성이 파이썬에서 어떤 타입으로 보이는지 먼저 선언
#   - mapped_column(...) --> DB 컬럼으로서의 설정을 지정
# ==========================================================================

# 클래스 안에서 타입을 적을 때, 그 클래스가 파일 아래쪽에 정의되어 있어도 
# 그냥 이름만 쓰는 것이 가능
from __future__ import annotations 

from datetime import date
from sqlalchemy import Date, Float, ForeignKey, String

# ---------------------------------------------------------------------------
# AssociationProxy, association_proxy

#  - team_player처럼 "중간 연결 테이블에 추가 데이터가 있는 다대다 관계"를 
#    다룰 때 사용
# ---------------------------------------------------------------------------
from sqlalchemy.ext.associationproxy import AssociationProxy, association_proxy

# ---------------------------------------------------------------------------
# Mapped[T] 
#     - 이 속성을 파이썬 코드에서 어떤 타입(T)로 다룰지 표시
# mapped_column(..) 
#     - 실제 DB 컬럼의 자료형/제약조건(기본기, 인덱스 등) 설정
# relationship(...)
#     - DB  컬럼이 아니라, 연결된 다른 ORM 객체로 이동하기 위한 "파이썬 전용" 속성
#     - DB에는 저장되지 않는다.
# ---------------------------------------------------------------------------
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database import Base # SQLAlchemy가 관리하는 테이블 

class Player(Base):
    """판타지 풋볼에서 선택할 수 있는 선수"""

    __tablename__ = 'player' # 실제 PostgreSQL 테이블 이름

    # 기본키(primary_key=True)
    player_id: Mapped[int] = mapped_column(primary_key=True, index=True)

    # Mapped[str | None] --> 값이 문자열이거나 없을 수도 있는 컬럼
    gsis_id: Mapped[str | None] = mapped_column(String) # NFL 공식 선수id
    first_name: Mapped[str] = mapped_column(String)
    last_name: Mapped[str] = mapped_column(String)
    position: Mapped[str] = mapped_column(String)

    # 이 행이 마지막으로 갱신된 날짜
    last_changed_date: Mapped[date] = mapped_column(Date)

    # ---------------------------------------------------------------------------
    # 1:N 관계 (선수 1명 : 성적 여러 건)
    #     relationship() --> DB 컬럼이 아니다.
    #     ex) Player.perfomances 라고 쓰면 이 선수의 Performance 객체 목록을
    #         파이썬의 리스트처럼 꺼내볼 수 있다라는 의미

    #     back_populates='player' --> 반대편(Performance 클래스)에서는 이 관계를
    #     player라는 이름으로 부른다. 짝 맞추기 표시
    # ---------------------------------------------------------------------------
    performances: Mapped[list[Performance]] = relationship(back_populates='player')

    # --------------------------------------------------------------------------------
    # N:M  관계 (선수 여러명 <-> 팀 여러 개) - 다대다 -> Association Object 패턴

    #     TeamPlayer 라는 클래스를 정식 ORM 클래스로 만들고, 각각 Player <-> TeamPlayer,
    #     Team <-> TeamPlayer 를 각각 1:N 관계로 연결한 뒤,
    #     TeamPlayer를 "연결 기록이 저장된 중간 다리"로 활용
        
    # cascade='all, delete-orphan'
    #     선수가 team_player 에서 제거되거나, 자체가 삭제되면, 관련된 TeamPlayer(가입 기록)
    #     행도 같이 정리한다. (고아 상태로 남은 team_player행이 안 생기게 한다.)
    # --------------------------------------------------------------------------------
    team_players: Mapped[list[TeamPlayer]] = relationship(
        back_populates='player',
        cascade='all, delete-orphan'
    )

    # --------------------------------------------------------------------------------
    # association_proxy
    #     team_players는 TeamPlayer(연결 기록) 객체의 리스트라서 "이 선수가 속한 팀 이름들만"
    #     "보고 싶다" --> player.team_players[0].team.team_name ??? 너무 길다 ㅠㅠ
    
    # association_proxy('team_players', 'team') 
    #     예전처럼 player.teams 라고만 써도 Team 객체 리스트를 바로 꺼내볼 수 있게 해주는
    #     "편의 통로"

    # creator=lambda team: TeamPlayer(team=team)
    #     player.teams.append(어떤팀)처럼 "쓰기"로 사용할 때, 내부적으로 어떤 
    #     TeamPlayer(team=팀, player=이 선수)를 자동으로 만들어서 연결해준다.
    # --------------------------------------------------------------------------------
    teams: AssociationProxy[list[Team]] = association_proxy(
        'team_players',
        'team',
        creator=lambda team: TeamPlayer(team=team),
    )

class Performance(Base):
    """선수 한 명의 특정 주차 판타지 성적(포인트)"""

    __tablename__ = 'performance'

    performance_id: Mapped[int] = mapped_column(primary_key=True, index=True)
    week_number: Mapped[str] = mapped_column(String) # 몇 주차 기록인지
    fantasy_points: Mapped[float] = mapped_column(Float) # 그 주차의 판타지 포인트점수
    last_changed_date: Mapped[date] = mapped_column(Date)

    # 외래키(ForeignKey) - DB 수준의 연결 --> 테이블명.컬럼명
    player_id: Mapped[int] = mapped_column(ForeignKey('player.player_id'))

    # relationship() - 파이썬 수준의 연결
    player: Mapped[Player] = relationship(back_populates='performances')

class League(Base):
    """여러 판타지 팀이 경쟁하는 리그"""

    __tablename__ = 'league'

    league_id: Mapped[int] = mapped_column(primary_key=True, index=True)
    league_name: Mapped[str] = mapped_column(String)
    scoring_type: Mapped[str] = mapped_column(String)
    last_changed_date: Mapped[date] = mapped_column(Date)

    # 1:N 관계 (리그 1개 : 팀 여러개)
    teams: Mapped[list[Team]] = relationship(back_populates='league')

class Team(Base):
    """사용자가 선수들을 조합해 만든 판타지 팀"""

    __tablename__ = 'team'

    team_id: Mapped[int] = mapped_column(primary_key=True, index=True)
    team_name: Mapped[str] = mapped_column(String)
    last_changed_date: Mapped[date] = mapped_column(Date)

    # 이 팀이 어느 리그 소속인지 - 외래키 (league 테이블 참조)
    league_id: Mapped[int] = mapped_column(ForeignKey('league.league_id'))

    league: Mapped[League] = relationship(back_populates='teams')

    # Player 클래스와 대칭되는 구조 -> 다대다 구조
    team_players: Mapped[list[TeamPlayer]] = relationship(
        back_populates='team',
        cascade='all, delete-orphan'
    )    

    # team.players --> team_players를 거치지 않고 바로 Player 객체 목록을 꺼내는 통로
    # creator= team.players.append(어떤선수)로 쓸 때 TeamPlayer(player=선수)를 자동생성
    players: AssociationProxy[list[Player]] = association_proxy(
        'team_players',
        'player',
        creator=lambda player: TeamPlayer(player=player),
    )    

class TeamPlayer(Base):
    """
    Team과 Player의 다대다 관계를 표현하는 연결(association) 테이블이면서,
    동시에 "이 연결이 언제 마지막으로 바뀌었는지"까지 저장하는 정식 ORM 클래스

    예전 버전 단순 secondary='team_player' 로 하면 last_changed_date 고아상태
    (team_id + player_id) --> 복합 기본키(composite primary key)
    독립된 ORM 클래스(Association Object)로 승격시켰다.
    
    """
    __tablename__ = 'team_player'

    # 복합 기본키
    team_id: Mapped[int] = mapped_column( # team테이블 안 team_id
        ForeignKey('team.team_id'), primary_key=True, index=True
    )
    player_id: Mapped[int] = mapped_column( # player테이블 안 player_id
        ForeignKey('player.player_id'), primary_key=True, index=True
    )

    # 언제 바뀌었는지 기록하는 컬럼 (기본값은 오늘날짜)
    last_changed_date: Mapped[date] = mapped_column(Date, default=date.today)

    team: Mapped[Team] = relationship(back_populates='team_players')
    player: Mapped[Player] = relationship(back_populates='team_players')

