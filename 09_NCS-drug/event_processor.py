#===============================================================
# 09_NCS-drug/event_processor.py
# 
#  의약품 연령금기 데이터 배치 처리
#
#  배치 처리 결과와 원본 데이터를 대상으로
#  조건에 맞는 이벤트를 탐지하여 이벤트 테이블에 저장한다.
#
# 이벤트 종류
# 1. AGE_OUT_OF_RANGE          : 특정연령 이상값
# 2. NON_INSURANCE_DRUG        : 비급여 의약품
# 3. ELDERLY_CONTRAINDICATION  : 노인 금기 의약품
#===============================================================
import argparse
from datetime import datetime

from sqlalchemy import text

from config import SOURCE_TABLE, EVENT_TABLE, AGE_THRESHOLD
from database import engine, check_required_tables, execute_sql

def init_event_table():
    execute_sql(
        f'''
        CREATE TABLE IF NOT EXISTS {EVENT_TABLE}(
        
        event_type VARCHAR(50) NOT NULL,
        product_name VARCHAR(255),
        company VARCHAR(255),
        detail TEXT,
        detected_at TIMESTAMP NOT NULL
        );
        '''
    )

def check_summary_ready():

    try:
        with engine.connect() as conn:
            conn.execute(
                text("SELECT 1 FROM drug_insurance_summary LIMIT 1")
            )
    except Exception as exc:
        raise RuntimeError(
            "배치 처리 결과가 없습니다."
            "batch_processor.py를 먼저 실행하세요."
        ) from exc

def detect_age_event(threshold):
    execute_sql(
        f''' 
        DELETE FROM {EVENT_TABLE}
        WHERE event_type='AGE_OUT_OF_RANGE';
        '''
    )
    execute_sql(
        f'''
        INSERT INTO {EVENT_TABLE}(
            event_type, product_name, company, detail, detected_at
        )
        SELECT
            'AGE_OUT_RANGE', "제품명", "업체명",
            CONCAT('특정연령=', "특정연령"),
            :detected_at
        FROM {SOURCE_TABLE}
        WHERE "특정연령" >= :threshold;
        ''',
        {
            "threshold": threshold,
            "detected_at": datetime.now()
        }
    )
    print (f'[event] 특정연령 이상 이벤트 탐지 완료(threshold={threshold})')

def detect_non_insurance_event():

    execute_sql(
        f'''
        INSERT INTO {EVENT_TABLE}(
            event_type, product_name, company, detail, detected_at
        )
        SELECT
            'NON_INSURANCE_DRUG',
            "제품명",
            "업체명",
            '비급여 의약품',
            :detected_at
        FROM {SOURCE_TABLE}
        WHERE "급여구분"='비급여';
        ''',
        {
            "detected_at": datetime.now()
        }
    )
    print('[event] 비급여 의약품 이벤트 탐지 완료')

def detect_elderly_event():

    execute_sql(
        f'''
        INSERT INTO {EVENT_TABLE}(
            event_type, product_name, company, detail, detected_at
        )
        SELECT
            'ELDERLY_CONTRAINDICATION',
            "제품명",
            "업체명",
            '노인 금기',
            :detected_at
        FROM {SOURCE_TABLE}
        WHERE "금기연령층"='노인';
        ''',
        {
            "detected_at": datetime.now()
        }
    )
    print("[event] 노인 금기 이벤트 탐지 완료")

def run_event_processing(age_threshold=AGE_THRESHOLD):
    check_required_tables()
    check_summary_ready()
    init_event_table()
    detect_age_event(age_threshold)
    detect_non_insurance_event()
    detect_elderly_event()
    print("[event] 이벤트 처리 완료")

def parse_args():

    parser = argparse.ArgumentParser(description="의약품 연령금기 데이터 이벤트 처리")
    parser.add_argument('--age-threshold', type=int, default=AGE_THRESHOLD)
    
    return parser.parse_args()

if __name__ == '__main__':
    args = parse_args()
    run_event_processing(age_threshold=65)

