#===========================================================
# storage_subway_busapi/01sybway/pipeline.py
# 
# 대구 지하철 수집 데이터를 저장하는 파이프라인 통합 실행
#   --> 처리단계를 지정(각각의 모듈들 함수들 호출)
#===========================================================

from database import init_db
from loader import load_from_csv
# <<검증 모듈>>

def main():
    print('1) 저장 구조 재설계(기본키 + UNIQUE 제약 적용)')
    init_db() # 함수 호출

    print()
    print('2) 결과 (subway_long.csv) 배치 적재')
    load_from_csv() #함수 호출

    print()
    print('3) 적재 검증')
    # 검증 함수 호출

if __name__ == '__main__':
    main()