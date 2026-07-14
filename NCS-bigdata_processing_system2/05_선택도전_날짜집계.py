# ================================================================================
# NCS-bigdata_processing_system/05_선택도전_날짜집계.py
#   [오늘의 복습 문제] 배치 처리 5번
#
#   - 날짜별 승차, 하차 집계
#   - 날짜, 승하차 구분 오름차순으로 조회 -> 같은 날짜 승차 합계와 하차 합계 차이가 큰 날짜

#  실행 : python 05_선택도전_날짜별집계.py
#  생성할 테이블명 : traffic_daily_summary
# ===========================================================================
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
    
def create_daily_summary() -> None:
    """날짜 와 승하차 구분별로 인원 값을 집계"""
    execute_sql(
        subway_engine,
        """
        DROP TABLE IF EXISTS traffic_daily_summary;

        CREATE TABLE traffic_daily_summary AS
        SELECT
            "날짜" AS use_date,
            "승하차" AS ride_type,
            COUNT(*) AS row_count,
            SUM("인원수") AS total_passengers
        FROM subway_raw
        GROUP BY "날짜", "승하차";

        CREATE INDEX idx_traffic_daily_summary_date_type
        ON traffic_daily_summary(use_date, ride_type);
        """
    )
    print('[batch] 날짜별 승하차 집계완료: traffic_daily_summary')

def main() -> None:
    print('[batch] 날짜별 배치 처리 시작')
    check_subway_input()
    create_daily_summary()
    print('[batch] 날짜별 배치 처리 완료')

if __name__ == '__main__':
    main()