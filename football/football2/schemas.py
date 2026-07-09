# ==========================================================================
# football/schemas.py
# 
# "API응답으로 어떤 모양의 JSON을 내보낼지"를 정의하는 파일
# 
# models.py의 SQLAlchemy 모델은 DB 테이블 구조를 표현한다.
# schemas.py의 Pydantic 모델은 클라이언트에게 보여줄 응답 구조를 표현한다.
#
# 같은 Player라는 이름을 쓰더라도 역할이 다르다!
# - models.Player : DB의 player 테이블과 매핑되는 ORM 클래스
# - schemas.Player : API 응답 JSON 모양을 검증/직렬화하는 Pydantic 클래스
#
# ==========================================================================
from pydantic import BaseModel, ConfigDict, Field
from typing import List
from datetime import date

# API 응답으로 내보낼 선수 성적 데이터 모양
class Performance(BaseModel):
    """
    from_attributes=True --> SQLAlchempy ORM 객체를 Pydantic 모델로 변환할 수 있게 한다.
    FastAPI가 응답모델 보고 ORM 객체의 속성을 읽어 JSON으로 바꾼다.
    """
    model_config = ConfigDict(from_attributes=True)
    performance_id : int
    player_id : int
    week_number : str
    fantasy_points : float
    last_changed_date : date

# 선수 기본 정보 - 다른 응답 모델에서도 재사용하기 위해 Base 클래스로 분리
class PlayerBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    player_id : int
    gsis_id : str | None
    first_name : str
    last_name : str
    position : str
    last_changed_date : date

# 선수 상세 응답 - 기본 정보에 성적 목록을 함께 포함한다.
class Player(PlayerBase):
    model_config = ConfigDict(from_attributes=True)

    # 빈 리스트 --> [] 를 클래스 변수 기본값으로 두면 여러 객체가 같은 리스트를 공유할 수 있어
    # 좋지 않다. Pydantic이 내부적으로 보호해주는 경우도 있지만, 안전한 패턴을 사용한다.
    performances : List[Performance] = Field(default_factory=list)

# 팀 기본 정보 - 리그 응답 안에 팀 목록을 넣을 때도 이 모델을 재사용
class TeamBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    league_id : int
    team_id : int
    team_name : str
    last_changed_date : date

# 팀 상세 응답 - 팀 기본 정보에 선수 목록을 함께 포함한다.
class Team(TeamBase):
    model_config = ConfigDict(from_attributes=True)

    # Team 응답에는 이 팀에 속한 선수 목록을 함께 담을 수 있다.
    players : List[PlayerBase] = Field(default_factory=list)

# 리그 응답 - 리그 기본 정보와 소속 팀 목록을 함께 반환
class League(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    league_id : int
    league_name : str
    scoring_type : str
    last_changed_date : date

    # 리그 응답에는 소속 팀 목록을 함께 담는다.
    # main.py /v0/leagues/{league_id} 응답에서 이 관계가 사용된다.
    teams : List[TeamBase] = Field(default_factory=list)

# 카운트 API 응답 전용 모델 - 테이블별 전체 개수를 담는다.
class Counts(BaseModel):
    league_count : int
    team_count : int
    player_count : int
    
