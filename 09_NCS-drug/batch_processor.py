#===============================================================
# 09_NCS-drug/batch_processor.py
# 
#  의약품 연령금기 데이터 배치 처리
#
#  저장되어있는 원본테이블을 대상으로
#  전체 데이터를 한 번에 집계하여 요약 테이블을 생성한다.
#
#===============================================================
from database import check_required_tables, execute_sql

from config import(
    SOURCE_TABLE,
    INSURANCE_SUMMARY_TABLE,
    AGEGROUP_SUMMARY_TABLE,
    COMPANY_SUMMARY_TABLE,
)

def create_insurance_summary() -> None:
    """급여구분(급여/비급여)별 의약품 개수를 집계한다."""
    
    execute_sql(
        f'''
        DROP TABLE IF EXISTS {INSURANCE_SUMMARY_TABLE};

        CREATE TABLE {INSURANCE_SUMMARY_TABLE} AS
        SELECT
            "급여구분" AS insurance_typ,
            COUNT(*) AS drug_count
        FROM {SOURCE_TABLE}
        GROUP BY "급여구분";

        CREATE INDEX idx_insurance_summary
        ON {INSURANCE_SUMMARY_TABLE} (drug_count DESC);
        '''
    )
    print('[batch] 급여 구분 집계완료')

def create_agegroup_summary() -> None:
    """금기연령층별 의약품 개수를 집계 한다."""
    
    execute_sql(
        f'''
        DROP TABLE IF EXISTS {AGEGROUP_SUMMARY_TABLE};

        CREATE TABLE {AGEGROUP_SUMMARY_TABLE} AS
        SELECT
            "금기연령층" AS age_group,
            COUNT(*) AS drug_count
        FROM {SOURCE_TABLE}
        GROUP BY "금기연령층";

        CREATE INDEX idx_agegroup_summary
        ON {AGEGROUP_SUMMARY_TABLE}(drug_count DESC);
        '''
    )
    print("[batch] 금기연령층 집계 완료")

def create_company_summary() -> None:
    """업체별 의약품 개수를 집계한다."""

    execute_sql(
        f'''
        DROP TABLE IF EXISTS {COMPANY_SUMMARY_TABLE};

        CREATE TABLE {COMPANY_SUMMARY_TABLE} AS
        SELECT
            "업체명" AS COMPANY,
            COUNT(*) AS drug_count
        FROM {SOURCE_TABLE}
        GROUP BY "업체명";

        CREATE INDEX idx_company_summary
        ON {COMPANY_SUMMARY_TABLE}(drug_count DESC);
        '''
    )
    print("[batch] 업체별 집계 완료")

def run_batch_processing() -> None:
    """ 배치 처리 전체 실행"""
    print('[batch] 필수 입력 테이블 확인')
    check_required_tables()
    create_insurance_summary()
    create_agegroup_summary()
    create_company_summary()
    print('[batch] 배치 처리 완료')

if __name__ == '__main__':
    run_batch_processing()