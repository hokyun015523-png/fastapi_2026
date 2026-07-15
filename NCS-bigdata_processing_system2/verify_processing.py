# ================================================================================
# NCS-bigdata_processing_system/verify_processing.py
#   - 배치/이벤트 처리 단계가 만들어낸 결과 테이블들이 실제로 존재하고
#     데이터가 채워졌는지 "최종점검"하는 스크립트1
#       
#
#     [데이터 품질 체크(data qulity check)]
#      처리 결과가 "0"건 이거나 테이블 자체가 없으면 파이프라인 어딘가
#      문제가 있다는신호이다. 이렇게 각 단계 끝에 "검증담계"를
#      따로 두는 것은 데이터 엔지니어링에서 매우 중요한 습관
# ================================================================================
from sqlalchemy import text
from database import subway_engine, bus_engine, table_count

# CHECKS - 무엇을 검증할지 데이터로 모아둔 리스트
CHECKS = [
    (subway_engine, 'traffic_subway_hourly_summary'), # 배치 처리 결과 : 시간대별 집계
    (subway_engine, 'traffic_subway_event_alerts'), # 이벤트 처리 결과 : 지하철 혼잡 알림
    (bus_engine, 'traffic_bus_area_summary'), # 배치처리 결과 : 지역별 버스 집계
    (bus_engine, 'traffic_bus_event_alerts'), # 이벤트 처리결과 : 버스 이상 알림
]

def verify() -> bool:
    """
    CHECKS에 정의된 모든 테이블을 순회하며 건수를 출력하고, 하나라도 조회에 실패하면 
    전체 결과를 FAIL로 판정

    반환값:
        True: 모든 테이블 조회에 성공(PASS)
        False: 하나 이상의 테이블 조회에 실패(FAIL)
    """
    print('=== 처리시스템 결과검증(배치+이벤트) ====')

    # 처음에는 성공(True)으로 가정하고, 실패를 한 번이라도 만나면 False
    ok = True

    for engine, table_name in CHECKS:
        try:
            count = table_count(engine, table_name) # 함수 호출
            print(f'{table_name}: {count:,}건')
        
        except Exception as exc:
            ok = False
            print(f'{table_name}: 확인 실패 - {exc}')

    print(f'검증 결과: {"PASS" if ok else "FAIL"}')

    # 호출한 코드가 화면 문자열을 다시 분석하지 않고도 성공 여부를 사용할 수 있게 bool값 반환
    return ok

if __name__ == '__main__':
    verify() # 검증 함수 호출