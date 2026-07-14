# ================================================================================
# NCS-bigdata_processing_system/03_시간대별승차집계.py
#   [오늘의 복습 문제] 배치 처리 3번
#
#   - 승차 데이터만 사용하여 시간대별 승차 인원을 집계합니다.
#
# 실행결과 : python 03_시간대별승차집계.py
# [batch] 시간대별 배치 처리 시작
# [batch] 입력 테이블 확인 완료: subway_raw 1,260,000건
# [batch] 시간대별 승차 집계 완료: traffic_hour_summary
# [batch] 시간대별 배치 처리 완료
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
    

def create_hour_summary() -> None:
    """승차 데이터만 시작 시간별로 집계한다."""
    execute_sql(
        subway_engine,
        """
        DROP TABLE IF EXISTS traffic_hour_summary;

        CREATE TABLE traffic_hour_summary AS
        SELECT
            "시작시" AS start_hour,
            COUNT(*) AS row_count,
            COUNT(DISTINCT "역번호") AS station_count,
            SUM("인원수") AS total_ride_passengers,
            ROUND(AVG("인원수")::numeric, 2) AS avg_ride_passengers
        FROM subway_raw
        WHERE "승하차" = '승차'
        GROUP BY "시작시";
    
        CREATE INDEX idx_traffic_hour_summary_total
        ON traffic_hour_summary(avg_ride_passengers DESC);
        """
    )
    print ('[batch] 시간대별 승차 집계 완료: traffic_hour_summary')

def main() -> None:
    print('[batch] 시간대별 배치 처리 시작')
    check_subway_input()
    create_hour_summary()
    print('[batch] 시간대별 배치 처리 완료')

if __name__ == '__main__':
    main()


# :: -> 이거는 형 변환을 하겠다는 뜻
# WHERE "승하차" = '승차' # "" -> 컬럼 / '' -> 문자열