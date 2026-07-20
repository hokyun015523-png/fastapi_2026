#===========================================================
# 09_NCS-drug/pipeline.py
#
# 의약품 연령금기 데이터 처리 시스템 통합
# 처리단계를 지정(각각의 모듈들 함수들 호출)
#===========================================================
from batch_processor import run_batch_processing
from event_processor import run_event_processing
from verify_processing import verify 

def main():
    print('====================')
    print('1) 배치 처리 (Batch Processing)')
    print('====================')
    run_batch_processing()
    print()

    print('====================')
    print('2) 이벤트 처리 (CEP)')
    print('====================')
    run_event_processing()
    print()

    print('===================')
    print('3) 처리 결과 검증 (Verification)')
    print('===================')
    verify()

if __name__ == '__main__':
    main()