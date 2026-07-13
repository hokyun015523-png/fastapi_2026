# ================================================================================
# NCS-bigdata_processing_system/02_역별집계.py
#   [오늘의 복습 문제] 배치 처리 2번
#
#   - 전체 지하철 데이터를 역별로 집계하는 배치 처리 프로그램을 작성
#
# 실행결과 : python 02_역별집계.py
# [batch] 역별 배치 처리 시작
# [batch] 입력 테이블 확인 완료: subway_raw 1,260,000건
# [batch] 역별 집계 완료: traffic_station_summary
# [batch] 역별 배치 처리 완료
#       
# ================================================================================
from database import subway_engine, execute_sql, table_count

# 1. 실행 전에 subway_raw 테이블의 존재 여부와 데이터 건수를 확인합니다.
def check_subway_input() -> None:
    """subway_raw 테이블의 존재 여부와 데이터 건수를 확인하는 함수"""
    try:
        count = table_count(subway_engine, 'subway_raw')
    except Exception as exc:
        raise RuntimeError("subway_raw 테이블을 확인할 수 없습니다."
                           "DB 연결과 원본 데이터 적재 여부를 확인하세요.") from exc
    
    if count == 0:
        raise RuntimeError("subway_raw 테이블에 데이터가 없습니다.")
    
    print(f'[batch] 입력 테이블 확인 완료: subway_raw {count:,}건')

# 2. `subway_raw`를 역 번호와 역 이름으로 묶습니다.
# 3. 역별 행 수, 인원 값 합계 및 평균을 계산합니다.
def create_station_summary() -> None:
    """원본 데이터를 역별로 집계 -> 결과 테이블로 만들기"""
    execute_sql(
        subway_engine,
        """
        DROP TABLE IF EXISTS traffic_station_summary;

        CREATE TABLE traffic_station_summary AS
        SELECT 
            "역번호" AS station_no,
            "역명" AS station_name,
            COUNT(*) AS row_count,
            SUM("인원수") AS total_passengers,
            ROUND(AVG("인원수")::numeric, 2) AS avg_passengers
        FROM subway_raw
        GROUP BY "역번호", "역명";

        CREATE INDEX idx_traffic_station_summary_total 
        ON traffic_station_summary(total_passengers DESC);
        """
    )
    print('[batch] 역별 집계 완료: traffic_station_summary')

def main() -> None:
    print('[batch] 역별 배치 처리 시작')
    check_subway_input()
    create_station_summary()
    print('[batch] 역별 배치 처리 완료')

if __name__ == '__main__':
    main()