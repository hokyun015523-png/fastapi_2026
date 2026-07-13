# ================================================================================
# NCS-bigdata_processing_system/batch_processor.py
#   - "배치 처리(Batch Processing)" 단계 예제 실습
#   - 저장시스템에 이미 적재되어 있는 원본 테이블(subway_raw, bus_stop) 전체를
#          한 번에 읽어서, 집계 결과 테이블을 새로 만든다.
#   
#   --> 배치 처리의 특징 : "전체 데이터를 대상으로, 정해진 시점에 한 번에" 처리
#       이번예제에서는 Python 코드가 데이터를 직접 계산하지 않고,
#       PostgreSQL에게 SQL을 실행시켜 DB 엔진이 집계하도록 위임한다.
#       데이터가 매우 클 때에는 이렇게 DB(또는 Spark) 쪽에서 처리하는 것이
#       Python으로 한 줄씩 읽어 계산하는 것보다 훨씬 빠르고 메모리 효율적이다.
# ================================================================================
from database import bus_engine, subway_engine, check_required_tables, execute_sql

def create_subway_hourly_summary() -> None:
    """
    지하철 원본 데이터(subway_raw)를 "역번호+역명+승하구분+시작시각" 기준으로
    그룹핑하여 시간대별 이용 인원 집계 테이블을 만든다.

    AVG("인원수")::numeric 
        --> AVG 결과값을 numeric타입으로 변환해라.
            PostgreSQL 문법
            CAST(AVG("인원수") AS numeric)이 표준 SQL문법    
    """
    execute_sql(
        subway_engine,
        '''
        DROP TABLE IF EXISTS traffic_subway_hourly_summary;

        CREATE TABLE traffic_subway_hourly_summary AS 
        SELECT
            "역번호" AS station_no,
            "역명" AS station_name,
            "승하차" AS ride_type,
            "시작시" AS start_hour,
            COUNT(*) AS row_count,
            SUM("인원수") AS total_passengers,
            ROUND(AVG("인원수")::numeric, 2) AS avg_passengers
        FROM subway_raw
        GROUP BY "역번호", "역명", "승하차", "시작시";

        CREATE INDEX idx_traffic_subway_hourly_summary_total
        ON traffic_subway_hourly_summary(total_passengers DESC);
        '''
    )
    print('[batch] 지하철 시간대별 집계 완료: traffic_subway_hourly_summary')

def create_bus_area_summary() -> None:
    """
    버스 정류소 원본 데이터(sub_stop)를 "위치구분(구/군)" 기준으로 집계하여 
    지역별 정류소 개수 및 좌표 누락 개수를 담은 테이블을 만든다.

    SQL 설명:
    - COALESCE('위치구분', '미분류') : '위치구분' 값이 NULL이면 '미분류' 문자열로 대체
    - COUNT(*) FILTER (WHERE 조건) : PostgreSQL의 '조건부집계' 문법. 그룹 전체 개수와 별도로
                그 그룹안에서 조건을 만족하는 행만 따로 세고 싶을 때 사용
    """
    execute_sql(
        bus_engine,
        '''
        DROP TABLE IF EXISTS traffic_bus_area_summary;

        CREATE TABLE traffic_bus_area_summary AS
        SELECT
            COALESCE("위치구분", '미분류') AS location_group,
            COUNT(*) AS stop_count,
            COUNT(*) FILTER (WHERE "위도" IS NULL OR "경도" IS NULL) AS null_coordinate_count
        FROM bus_stop
        GROUP BY COALESCE("위치구분", '미분류');

        CREATE INDEX idx_traffic_bus_area_summary_count
        ON traffic_bus_area_summary(stop_count DESC);
        ''',
    )
    print('[batch] 버스 위치구분별 집계 완료 : traffic_bus_area_summary')

def run_batch_processing() -> None:
    """
    배치 처리 전체 흐름을 순서대로 실행하는 엔트리포인트(프로그램이 실행을 시작하는 지점) 함수
    
    실행 순서:
        1) check_required_tables() : 원본 테이블이 준비되었는지 확인
        2) create_subway_hourly_summary() : 지하철 집계 테이블 생성
        3) create_bus_area_summary() : 버스 집계 테이블 생성

    작은 단위로 쪼개고, 함수가 순서대로 호출하는 구조는 pipeline.py에서 
    batch / realtime / event 단계를 조립할 때 재사용하기 쉽다.
    """
    print('[batch] 필수 입력 테이블 확인')
    check_required_tables()
    create_subway_hourly_summary()
    create_bus_area_summary()
    print('[batch] 배치 처리 완료')

# 이 파일을 python batch_processor.py 처럼 직접 실행했을 때만 아래 코드가 동작한다.
# (다른 파일에서 import batch_processor 로 불러올 때는 실행되지 않는다. 
#   모듈 재사용을 위한 관용구)
if __name__ == '__main__':
    run_batch_processing() # 엔트리포인트 함수 호출