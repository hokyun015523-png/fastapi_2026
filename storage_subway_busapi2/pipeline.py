#===========================================================
# storage_subway_busapi/02_bus/pipeline.py
# 
# 대구 버스 노선 수집 데이터를 저장하는 파이프라인 통합 실행
#   --> 처리단계를 지정(각각의 모듈들 함수들 호출)
#===========================================================
from database import init_db
from loader import load_from_csv
from verity import verify

def main():
    print('1) 저장 구조 준비 (정류장ID 기본키)')
    init_db()

    print()
    print('2) bus_stop.csv 적재(merge upsert)')
    load_from_csv()

    print()
    print('3) 적재 검증')
    verify()

if __name__ == '__main__':
    main()

print(__name__)