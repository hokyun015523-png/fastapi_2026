# ===========================================================
# storage_subway_busapi/01_subway/verify.py
#
#   지허철 적재 검증
#       - 필수 컬럼 NULL 여부
#       - 인원수 음수 여부
#       - 시작시 범위 0~23 여부
#       - 승하차 허용값 여부
#       - 업무 키 조합 중복 여부
#
# 커넥션(connection) ??
# - 파이썬 프로그램과 PostgreSQL 서버 사이에 맺어지는 연결 통로
# - 계속 SQL을 주고 받으려면 이 연결부터 먼저 맺는다.
#   - 연결 생성 -> 쿼리 실행 -> 연결 종료 --> 낭비
#
# DB 커넥션 풀(Connection Pool) ??
# - 프로그램이 시작될 때(create_engine(...) 호출 시점) 연결 여러개를 미리 만들어서 
# "풀(pool, 저장소)"에 담아 둔다.
# - engine.connect()를 호출하면, 새로 연결을 만드는 게 아니라 풀에서 이미 만들어진
#    연결을 잠깐 빌려온다.
# - 다 쓰고 나면 (with 블록이 끝나면) 연결을 끊는게 아니라 풀에 다시 반납해서,
#    다음 번 요청이 그 연결을 재사용할 수 있게 한다.
# ===========================================================================

from sqlalchemy import text
from database import engine

def verify():
    # engine.connect()로 커넥션을 열고,  with 블록을 벗어나면 자동으로 연결 반환(close됨)
    with engine.connect() as conn:

        # --- 1. 전체 적재 건수 확인 ---
        # .scalar() --> 결과에서 첫번째 행의 첫번째 컬럼 값 하나만 뽑아온다.
        #               (값이 하나만 나오는 쿼리에 사용)
        total = conn.execute(text("SELECT COUNT(*) FROM subway_raw")).scalar()

        # --- 2. 필수 컬럼별 NULL 개수 확인 ---
        # FILTER (WHERE 조건) --> 하나의 SELECT 안에서 조건별로 COUNT를 따로 집계하는
        #                           PostgreSQL의 문법
        null_check = conn.execute(text("""
            SELECT
                COUNT(*) FILTER (WHERE 역번호 IS NULL) AS null_station_no,
                COUNT(*) FILTER (WHERE 역명 IS NULL) AS null_station_name,
                COUNT(*) FILTER (WHERE 날짜 IS NULL) AS null_date,
                COUNT(*) FILTER (WHERE 시간대컬럼 IS NULL) AS null_time_col,
                COUNT(*) FILTER (WHERE 승하차 IS NULL) AS null_inout,
                COUNT(*) FILTER (WHERE 인원수 IS NULL) AS null_count,
                COUNT(*) FILTER (WHERE 시작시 IS NULL) AS null_start_hour
            FROM subway_raw
            """)).fetchone() # 결과가 7개의 컬럼으로 이루어진 한 행이므로, 튜플 형태의 행 하나를 가져온다
        
        # --- 3. 인원수 음수 여부 확인 ---
        negative_count = conn.execute(text("""
            SELECT COUNT(*) FROM subway_raw 
            WHERE 인원수 < 0
        """)).scalar()

        # --- 4. 시작시 (시간) 범위 이탈 확인 ---
        # 시작시는 0~23시 범위 (24시간제 기준) --> BETWEEN 0 AND 23
        invalid_hour = conn.execute(text("""
            SELECT COUNT(*) FROM subway_raw
            WHERE 시작시 NOT BETWEEN 0 AND 23                            
        """)).scalar()

        # --- 5. 승하차 값 유효성 확인 ---
        # 반드시 '승차' 또는 '하차' 둘 중 하나의 문자열이어야 한다.
        invalid_inout = conn.execute(text("""
            SELECT COUNT(*) FROM subway_raw
            WHERE 승하차 NOT IN ('승차', '하차')
        """)).scalar()

        # --- 6. 업무 키(business key) 조합 중복 확인 ---
        # 업무 키 = 역번호 + 날짜 + 시간대컬럼 + 승하차 
        #   이 4개의 컬럼이 같으면 논리적으로 동일한 레코드(행) --> 중복 적재로 간주
        #       서브쿼리에서 GROUP BY로 묶은 뒤, HAVING절을 사용해서 
        #       "2건 이상 중복된 키 조합"만 걸러내고, 바깥 쿼리에서 그 조합의 개수를 센다.
        #       "중복된 원본 행의 총 개수"가 아니라,
        #       "중복이 발생한 키 조합의 가짓수"를 알고싶다!
        duplicate_count = conn.execute(text("""
            SELECT COUNT(*)
            FROM (
                SELECT 역번호, 날짜, 시간대컬럼, 승하차, COUNT(*) AS cnt
                FROM subway_raw
                GROUP BY 역번호, 날짜, 시간대컬럼, 승하차
                HAVING COUNT(*) > 1
            ) t
        """)).scalar()

    # --- 7. 검증 결과 출력 ---
    print('==== 지하철 적재 검증 결과 ====')
    print(f'전체 건수 : {total:,}')
    print(f'역번호 NULL 건수 : {null_check[0]}')
    print(f'역명 NULL 건수 : {null_check[1]}')
    print(f'날짜 NULL 건수 : {null_check[2]}')
    print(f'시간대컬럼 NULL 건수 : {null_check[3]}')
    print(f'승하차 NULL 건수 : {null_check[4]}')
    print(f'인원수 NULL 건수 : {null_check[5]}')
    print(f'시작시 NULL 건수 : {null_check[6]}')
    print(f'인원수 음수 건수 : {negative_count}')
    print(f'시작시 범위 이탈 건수 : {invalid_hour}')
    print(f'승하차 이상값 건수 : {invalid_inout}')
    print(f'중복 키 건수 : {duplicate_count}')

    # --- 8. 최종 PASS/FAIL 판정 ---
    ok = (
        total > 0
        and all(value == 0 for value in null_check) # 모든 컬럼이 0이어야 통과
        and negative_count == 0
        and invalid_hour == 0
        and invalid_inout == 0
        and duplicate_count == 0
    )
    print(f'검증 결과 : {"PASS" if ok else "FAIL"}')
    return ok
    
if __name__ == '__main__':
    verify()