# ==========================================================
# football/seed_postgres_basic.py
#
# football/data/ 안 csv5개를 PostgreSQL 데이터베이스에 적재하는 초기화 스크립트 
#   test_crud.py는 csv파일을 직접 읽지 않는다. 
#   PostgreSQL DB에 이미 들어가 있는데이터를 조회해서 테스트 한다.
#   따라서 테스트를 실행하기 전에 이 파일을 한번 실행해서 csv 데이터를 
#   PostgreSQL테이블에 넣어두어야 한다.

#   실행 할때마다 기존 테이블을 drop_all()로 삭제하고 다시 만든다
#   DB에 중요한 데이터가 있다면 절대 실행하면 안된다.

# ==========================================================
from __future__ import annotations  # 자료형에 주는것 처음 작성한다

import csv                          # 파이썬 표준라이브러리
from datetime import date
from pathlib import Path

from sqlalchemy.orm import Session  # 외부 라이브러리

from database import Base, engine   # 우리가 만든 
import models 

# 현재 파일이 들어있는 football 폴더의 절대 경로
#   (어느 위치에서 실행하더라도 data 폴더를 안정적으로 찾기위해 사용한다)
BASE_DIR = Path(__file__).resolve().parent

# csv 원본 데이터가 들어있는 폴더 
DATA_DIR = BASE_DIR / "data"

def parse_date(value: str) -> date: # -> 이건 리턴되는 값
    """
    CSV에서 읽은 날짜 문자열을 Python date 객체로 변환한다.

        CSV 파일 안의 날짜는 "2024-04-18" 같은 문자열이다.
        models.py의 last_changed_date 컬럼은 SQLAlchemy Date 타입이다.
        DB에 넣기 전에 문자열을 date객체로 바꿔주는 것이 안전하다.
    """
    return date.fromisoformat(value)

def read_rows(filename: str) -> list[dict[str, str]]:
    """
    csv파일 하나를 읽어서 딕셔너리 리스트로 변환

    {
        "player_id":"1001"
        "gsis_id":"00-00234569"
        "first_name":"Aaron",
        ...
    }

    csv.DictReader는 첫 줄의 컬럼명을 key로 사용하므로
    row["player_id"] 처럼 컬럼명으로 값ㅇ르 꺼낼 수 있다.

    """
    path = DATA_DIR / filename
    with path.open(newline="", encoding="utf-8") as file:
        return list(csv.DictReader(file))

def seed() -> None:
    """
    PostgreSQL 테이블을 새로 만들고, CSV 데이터를 순서대로 적재한다.

    적재 순서가 중요
    테이블 사이에는 외래키(Foreignkey)
    
    - team.league_id는 league.league_id를 참조한다.
    - performance.player_id는 player.player_id를 참조한다.
    - team_player.team_id는 team.team_id를 참조한다
    - team_player.player_id는 player.player_id를 참조한다
        참조 당하는 부모 테이블을 먼저 넣고,
            참조 하는 자식테이블을 나중에 넣어야한다.
    
    """
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    # Session은 SQLAlchemy ORM 객체를 DB에 저장하는 작업 공간
    # with 블록을 쓰면 작업이 끝난뒤 세션이 자동으로 정리
    with Session(engine) as session:
        # 1. player 테이블 적재
        #    player는 performance와 team_player에서 참조하므로 먼저 넣는다
        players = [
            models.Player(
                player_id=int(row["player_id"]),
                gsis_id=row["gsis_id"] or None,
                first_name=row["first_name"],
                last_name=row ["last_name"],
                position=row["position"],
                last_changed_date=parse_date(row["last_changed_date"])
            )
            for row in read_rows("player_data.csv")
        ]
        session.add_all(players)

        # 2. league 테이블 적재 - league는 team에서 참조하므로 team보다 먼저
        leagues = [
            models.League(
                league_id=int(row["league_id"]),
                league_name=row["league_name"],
                scoring_type=row["scoring_type"],
                last_changed_date=parse_date(row["last_changed_date"])
            )
            for row in read_rows("league_data.csv")
        ]
        session.add_all(leagues)

        # flush()아직 commit은 하지 않았지만, 현재 세션에 쌓인 INSERT를 DB로 보낸다.
        # player와 league 행이 같은 트랜잭션 안에서 실제 테이블에 먼저 보이게 된다.
        # 뒤에서 team, team_player 처럼 외래키를 가진 테이블을 넣을 때
        # 참조할 부모 행이 아직 없다는 오류를 피하고, 실행 순서 파악도 쉽다. 
        session.flush()

        # 3. team 테이블 적재 - Team은 league_id를 통해 League에 속한다.
        teams = [
            models.Team(
                team_id=int(row["team_id"]),
                team_name=row["team_name"],
                league_id=int(row["league_id"]),
                last_changed_date=parse_date(row["last_changed_date"])
            )
            for row in read_rows("team_data.csv")
        ]
        session.add_all(teams)

        session.flush()
        

        # 4.team_player 연결 테이블 적재
        # Team과 Player의 다대다 관계를 표현하는 중간 테이블
        team_players = [
            models.TeamPlayer(
                team_id=int(row["team_id"]),
                player_id=int(row["player_id"]),
                last_changed_date=parse_date(row["last_changed_date"])
            )
            for row in read_rows("team_player_data.csv")
        ]
        session.add_all(team_players)

        # 5. performance 테이블 적재
        # Performance는 player_id로 Player를 참조한다.
        performances = [
            models.Performance(
                performance_id=int(row["performance_id"]),
                week_number=row["week_number"],
                fantasy_points=float(row["fantasy_points"]),
                player_id=int(row["player_id"]),
                last_changed_date=parse_date(row["last_changed_date"])
            )
            for row in read_rows("performance_data.csv")
        ]
        session.add_all(performances)

        # SQLAlchemy 세션에 "저장 예정" 상태로 올라간 것이다.
        # commit()을 호출해야 PostgreSQL 테이블에 INSERT가 반영된다
        session.commit()

    print('[seed] PostgreSQL 초기 데이터 적재 완료')
    print(f'[seed] player: {len(players):,} rows')
    print(f'[seed] league: {len(leagues):,} rows')
    print(f'[seed] team: {len(teams):,} rows')
    print(f'[seed] team_player: {len(team_players):,} rows')
    print(f'[seed] performance: {len(performances):,} rows')

if __name__ == "__main__":
    # 이파일을 직접 실행했을 때만 seed()를 호출
    # 다른 파일에서 inport 할 때 DB 초기화가 자동 실행되는것을 막아준다.
    seed()