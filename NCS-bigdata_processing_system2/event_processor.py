# ================================================================================
# NCS-bigdata_processing_system/event_processor.py
#   - "이벤트 처리(Event Processing / CEP)" 예제
#       배치 처리 결과와 원본 데이터를 대상으로 "이상 상황(조건을 만족하는 사건)"을
#       탐지하여 별도의 알림(alert) 테이블에 기록한다.
#
#   - 이벤트 처리는 조건(규칙)을 만족하는 사건을 찾아내는 것이 핵심이다.
#       1) SUBWAY_CONGESTION : 특정 역/시간대 이용객이 임계값 이상인 [혼잡]이벤트
#       2) BUS_COORDINATE_OUT_OF_RANGE : 버스 정류소 좌표가 대구 범위를 벗어난
#                                        [이상 데이터]이벤트
#       3) BUS_LOCATION_GROUP_INVALID : 버스 정류소 "위치구분" 값이 허용 목록에 
#                                        없는 이벤트
#
#   - 실무의 CEP(Complex Event Processing) 엔진(Esper, Flink CEP 등)은 이런 규칙을
#     스트림에 실시간으로 적용하지만, 여기서는 SQL의 WHERE 조건으로 같은 개념을 단순화
#
#   * SQL 보안 용어 *
#   1) SQL 인젝션 (SQL Injection)
#       SQL 문자열에 신뢰할 수 없는 값을 직접 이어 붙일 때, 그 값이 단순 데이터가 아니라
#       SQL 문법으로 해석되어 원래 의도와 다른 명령이 실행되는 보안 취약점
#   
#   2) 바인드 파라미터(bind parameter)
#       SQL 문장에 :threshold 처럼 "값이 들어갈 자리"만 표시하고,
#       실제 파이썬 값은 별도의 딕셔너리로 DB 드라이버에 전달하는 방식
#       임계값, 날짜, 이름처럼 "데이터 값"을 바인딩 한다.
#       테이블명, 컬럼명, ASC/DESC 같은 "SQL 구조"는 보통 값 파라미터로 바인딩할 수 없다.
#       --> 허용 목록(화이트리스트)으로 검증
#   
#   3) 멱등성(idempotency)
#       같은 초기화 코드를 여러번 실행해도 결과가 망가지지 않는다. 
# ================================================================================
import argparse  # 파이썬 프로그램을 실행할 때 터미널에서 전달한 옵션을 읽는 표준 라이브러리
from datetime import datetime

from sqlalchemy import text

from config import BUS_LOCATION_GROUPS, DAEGU_LAT_MAX, DAEGU_LAT_MIN, DAEGU_LON_MAX, DAEGU_LON_MIN
from database import bus_engine, check_required_tables, execute_sql, subway_engine

def init_subway_alert_table() -> None:
    """
    지하철 혼잡 이벤트 알림을 저장할 테이블을 준비(없으면 생성)

    컬럼 설명:
        event_type : 이벤트 종류
        station_name : 어느 역에서 발생했는지
        ride_type : 승차/하차 구분
        start_hour : 몇 시 대인지(시간대 0~23)
        metric_value : 실제 측정된 값(총 이용객 수)
        threshold_value : 이벤트로 판정된 기준값(임계값)
        detected_at : 언제 이 이벤트가 탐지 되었는지
    
    """
    execute_sql(
        subway_engine,
        """
        CREATE TABLE IF NOT EXISTS traffic_subway_event_alerts (
            id BIGSERIAL PRIMARY KEY,
            event_type VARCHAR(50) NOT NULL,
            station_name VARCHAR(100) NOT NULL,
            ride_type VARCHAR(20) NOT NULL,
            start_hour INTEGER NOT NULL,
            metric_value BIGINT NOT NULL,
            threshold_value BIGINT NOT NULL,
            detected_at TIMESTAMP NOT NULL
        );
        """
    )

def init_bus_alert_table() -> None:
    """
    버스 정류소 관련 이상 이벤트 알림을 저장할 테이블을 준비 (없으면 생성)

        - TEXT : 길이를 미리 정하지 않는 PostgreSQL 문자열 타입
    
    """
    execute_sql(
        bus_engine,
        """
        CREATE TABLE IF NOT EXISTS traffic_bus_event_alerts (
            id BIGSERIAL PRIMARY KEY,
            event_type VARCHAR(50) NOT NULL,
            stop_id VARCHAR(50),
            stop_name VARCHAR(200),
            detail TEXT NOT NULL,
            detected_at TIMESTAMP NOT NULL
        );
        """
    )

def detect_subway_congestion(threshold: int) -> None:
    """
    배치 집계 결과(traffic_subway_hourly_summary)에서 total_passengers(총 이용객)가
    threshold(임계값) 이상인 행을 찾아 "혼잡 이벤트"로 등록
    """
    execute_sql(
        subway_engine,
        """
        DELETE FROM traffic_subway_event_alerts 
        WHERE event_type = 'SUBWAY_CONGESTION';

        """
    )
    execute_sql(
        subway_engine,
        """
        INSERT INTO traffic_subway_event_alerts(
            event_type, station_name, ride_type, start_hour,
            metric_value, 
            threshold_value, 
            detected_at
        )
        SELECT
            'SUBWAY_CONGESTION', station_name, ride_type, start_hour, 
            total_passengers,
            :threshold,      -- 저장할 임계값 자리: 아래 params["threshold"]와 연결
            :detected_at     -- 탐지 시각 자리: 아래 params["detected_at"]과 연결
        FROM traffic_subway_hourly_summary
        WHERE total_passengers >= :threshold;

        """,
        # SQL 문자열과 값 딕셔너리를 별도로 전달하는 것이 바인딩의 핵심 (안전)
        {"threshold": threshold, "detected_at": datetime.now()}
    )
    print(f'[event] 지하철 혼잡 이벤트 탐지 완료 threshold={threshold:,}')

def check_subway_summary_ready() -> None:
    """
    이벤트 처리는 배치 처리 결과(traffic_subway_hourly_summary)를 입력으로 사용하므로
    이 테이블이 먼저 만들어져야 한다. 실행 순서를 알려주는 함수
    """
    try:
        with subway_engine.connect() as conn:
            conn.execute(text("SELECT 1 FROM traffic_subway_hourly_summary LIMIT 1"))

    except Exception as exc:
        raise RuntimeError(
            "traffic_subway_hourly_summary 테이블이 없습니다."
            "event_processor.py 실행 전에 batch_processor.py를 먼저 실행하세요."
        ) from exc
    
def detect_bus_coordinate_events() -> None:
    """
    버스정류소 원본(bus_stop) 데이터에서 두 종류 이벤트를 탐지

    1) BUS_COORDINATE_OUT_OF_RANGE
        위도/경도가 NULL이거나, 대구 범위를 벗어난 정류소를 찾는다.

    2) BUS_LOCATION_GROUP_INVALID
        "위치구분" 값이 NULL이거나, BUS_LOCATION_GROUPS에 없는 값이면 이상 데이터로 간주 
    
    """
    execute_sql(bus_engine, "DELETE FROM traffic_bus_event_alerts;")
    execute_sql(
        bus_engine,
        """
        INSERT INTO traffic_bus_event_alerts (
            event_type, stop_id, stop_name, detail, detected_at
        )
        SELECT
            'BUS_COORDINATE_OUT_OF_RANGE', "정류소ID", "정류소명", 
            CONCAT('lat=', "위도", ', lon=', "경도"),
            :detected_at
        FROM bus_stop
        WHERE "위도" IS NULL OR "경도" IS NULL 
            OR "위도" NOT BETWEEN :lat_min AND :lat_max
            OR "경도" NOT BETWEEN :lon_min AND :lon_max;
        """,
        {
            "lat_min": DAEGU_LAT_MIN,
            "lat_max": DAEGU_LAT_MAX,
            "lon_min": DAEGU_LON_MIN,
            "lon_max": DAEGU_LON_MAX,
            "detected_at": datetime.now()
        }
    )
    # ex) ["'남구'", "'북구'"] 
    allowed_values = ', '.join(f"'{value}'" for value in sorted(BUS_LOCATION_GROUPS))
    execute_sql(
        bus_engine,
        f"""
        INSERT INTO traffic_bus_event_alerts (
            event_type, stop_id, stop_name, detail, detected_at
        )
        SELECT
            'BUS_LOCATION_GROUP_INVALID', "정류소ID", "정류소명",
            CONCAT('location_group=', COALESCE("위치구분", 'NULL')),
            :detected_at
        FROM bus_stop
        WHERE "위치구분" IS NULL OR "위치구분" NOT IN ({allowed_values});
        """,
        {"detected_at": datetime.now()}
    )
    print('[event] 버스 좌표/위치구분 이벤트 탐지 완료')

def run_event_processing(subway_threshold: int = 100000) -> None:
    """이벤트 저리 전체 흐름을 실행하는 엔트리포인트 함수"""
    check_required_tables()  # 원본 테이블 준비 여부 확인
    check_subway_summary_ready()  # 배치 처리 결과(집계 테이블) 준비 여부 확인
    init_subway_alert_table()  # 지하철 알림 테이블 생성
    init_bus_alert_table()  # 버스 알림 테이블 생성
    detect_subway_congestion(subway_threshold)  # 지하철 혼잡 이벤트 탐지
    detect_bus_coordinate_events()  # 버스 좌표/위치구분 이벤트 탐지
    print('[event] 이벤트 처리 완료')

def parse_args() -> argparse.Namespace:
    """
    argparse 라이브러리를 이용해 커맨드라인 인자를 처리하는 함수

    예) python event_processor.py --subway-threshold 50000
    -> 임계값을 50000명으로 낮춰서 더 많은 혼잡 이벤트를 탐지하도록 실행

    # ArgumentParser 객체 생성
    ArgumentParser(description='설명글") 
    --help 실행 시 상단에 표시되는 설명 문구

    # --subway-threshold 옵션 등록
    .add_argument() 함수 : 옵션값, 자료형(타입), 디폴트값(기본값) 설정
    
    """
    parser = argparse.ArgumentParser(description='교통 데이터 이벤트 처리')

    # type을 설정하지 않으면 기본값이 문자열
    parser.add_argument('--subway-threshold', type=int, default=100000)

    return parser.parse_args() # 실제 실행 시 입력된 값을 읽어서 객체로 반환

if __name__ == '__main__':
    args = parse_args()  
    run_event_processing(subway_threshold=args.subway_threshold)