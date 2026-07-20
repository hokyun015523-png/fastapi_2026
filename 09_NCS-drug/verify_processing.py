# ================================================================================
# drug_processing/verify_processing.py
#
# 배치 처리 및 이벤트 처리 결과 검증
#
# 생성된 테이블이 존재하는지,
# 데이터가 정상적으로 저장되었는지 확인한다.
# ================================================================================

from database import engine, table_count

CHECKS = [

    # 원본 데이터
    "drug_age",

    # 배치 처리 결과
    "drug_insurance_summary",
    "drug_agegroup_summary",
    "drug_company_summary",

    # 이벤트 처리 결과
    "drug_event_alert"
]


def verify() -> bool:
    """
    처리 결과 테이블을 순서대로 확인한다.

    반환값
        True  : PASS
        False : FAIL
    """
    print("=" * 60)
    print("의약품 연령금기 데이터 처리 결과 검증")
    print("=" * 60)

    ok = True

    for table_name in CHECKS:

        try:
            count = table_count(table_name)
            print(f'{table_name} : {count:,}건')
        except Exception as exc:
            ok = False
            print(f'{table_name} : 확인 실패 ({exc})')

    print("=" * 60)
    print(f'검증 결과 : {"PASS" if ok else "FAIL"}')
    print("=" * 60)

    return ok

if __name__ == "__main__":

    verify()