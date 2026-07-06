#===========================================================
# storage_subway_busapi/01sybway/loader.py
# 
# 수집한 결과로 나온 파일 subway_long.csv을
# subway_raw 테이블에 적제
#===========================================================

# 라이브러리 불러오기
import os
import pandas as pd
from sqlalchemy.dialects.postgresql import insert as pg_insert
from database import engine
from models import SubwayRaw

# 경로 설정 및 기본값 설정
BASE_DIR = os.getcwd()
INPUT_PATH = os.path.join(BASE_DIR, 'input', 'subway_long.csv')
CHUNK_SIZE = 5000

# CSV -> 배치 적재

# 주말 여부  --> 주말이다 / 아니다
# 파이썬은 bool("False")--> 파이썬 입장에서는 "비어있지 않은 문자열"이라서 참
# 이런 문제를 예방하기 위해서 딕셔너리로 명시적 변환
WEEKEND_MAP = {
    True: True, False: False, # 이미 파이썬 bool자료형인경우
    "True": True, "False": False, # 문자열 "True"/"False" (첫 글자 대문자)
    "TRUE": True, "FALSE": False, # 전부 대문자인 경우
    "true": True, "false": False, # 전부 소문자인 경우
    "1": True, "0": False, # 문자열 숫자로 들어온 경우
    1: True, 0: False, # 정수로 들어온 경우
}

# 함수 정의
# 함수 이름 앞에 _가 붙어 있는 경우
#   loader.py 내부에서만 쓰는 헬퍼(보조) 함수
#   다른 쪽 파일에서는 이 함수들을 직접 호출할 일이 없다!
#   private 함수 같은 느낌 (다른 언어처럼 강제되지 않는다)
#   내부에서 주로 사용하는 용도니,
#   외부에서는 직접 가져다 사용하지 말라
def _to_bool(value):
    """WEEKEND_MAP에 없는 값(예상치 못한 이상값)이 들어오면 에러를 내지않고 기본값 False로"""
    return WEEKEND_MAP.get(value, False)

def _prepare_chunk(chunk: pd.DataFrame) -> list[dict]:
    """
    pandas로 읽어온 CSV 한 덩어리(chunk)를 DB에 바로 넣을  수 있는 
    딕셔너리 리스트 형태로 가공하는 함수
    """
    chunk = chunk.copy() # 원본 chunk 직접 건드리면 pandas에서 경고

    #'날짜' 컬럼을 문자열 등에서 실제 datetime형으로 변환 후,
    # 시간 정보는 버리고 날짜 (date)형만 남긴다.
    # errors='coerce' --> 변환 불가능한 것은 에러 대신 결측치로 처리
    chunk['날짜'] = pd.to_datetime(chunk['날짜'], errors='coerce').dt.date
    chunk['주말여부'] = chunk['주말여부'].map(_to_bool)

    # 핵심 컬럼(역번호, 날짜, 시간대컬럼, 승하차) 중 하나라도 비어있으면
    # UNIQUE 제약이나 흐름상 의미가 없으므로 통째로 제거
    chunk = chunk.dropna(subset=['역번호', '날짜', '시간대컬럼', '승하차'])

    # 필요한 컬럼만 순서대로 골라, DB 삽입에 사용할 수 있는 딕셔너리 리스트로 변환
    # (SQLAlchemy Core의 insert(values=[...])형태로 넣기 위해서)
    return chunk[[
        '월', '일', '역번호', '역명', '승하차', '시간대컬럼', '인원수', '시작시', '날짜',
        '요일코드', '주말여부', 
    ]].to_dict(orient='records') # 행단위로 하나씩 딕셔너리 만든다

# 함수 정의
def load_from_csv(path: str=INPUT_PATH, chunksize: int=CHUNK_SIZE) -> dict:
    """
    CSV 파일을 배치 단위로 읽어 subway_raw 테이블에 적재하는 메인함수

    매개변수(파라미터)
    path: str
        -->읽어들일 CSV파일 경로
    chunksize: int
        --> 한 번에 읽어서 처리할 행의 개수(배치 크기)

    반환값(리턴값)
    dict
        {"success": 신규 적재 건수, "skipped_duplicate": 중복 스킵 건수, "failed": 실패 건수}

    """
    # 전체 적재 결과를 누적할 카운터들
    total_success = 0 # 새로 삽입된 건수
    total_skipped = 0 # UNIQUE 제약에 걸려 중복으로 스킵된 건수
    total_failed = 0 #배치 자체가 에러로 실패한 건수

    for i, chunk in enumerate(pd.read_csv(INPUT_PATH, encoding='utf-8-sig', chunksize=CHUNK_SIZE)):
        try:
            # 이번 배치(데이터를 한번에 처리하지 않고 일정한 묶음 단위로 처리)를 
            # DB 삽입용 딕셔너리 리스트로 가공
            records = _prepare_chunk(chunk) # 함수 호출

            # 가공후 남은 데이터가 없다면 (전부 결측 등으로 걸러졌다면) 이번 배치는 건너뛴다.
            if not records:
                continue

            with engine.begin() as conn:
                #PostgreSQL 전용 insert 구문 생성
                stmt = pg_insert(SubwayRaw).values(records)

                # UNIQUE 제약에 위반회는 행은 에러를 내지 않고 그냥 무시(skip) 하도록 설정
                stmt = stmt.on_conflict_do_nothing(constraint='uq_subway_raw_key')

                # 실제 SQL실행
                result = conn.execute(stmt)

            # rowcount : 실제로 삽입된 행의 갯수(충돌로 스팁된 행은 포함하지 않는다)
            # 일부 환경에서는 rowcount가 None일 수 있어 방어적으로 처리 (0표시)
            inserted = result.rowcount if result.rowcount is not None else 0

            #중복이라 스킵된건수 ==> 이번 배치에서 시도한 건수 - 실제 삽입된 건수
            skipped = len(records) - inserted

            total_success += inserted
            total_skipped += skipped

            print(f'{i+1}번째 배치 - 신규 {inserted}건 / 중복스킵 {skipped}건')

        except Exception as e:
            # 예상치 못한 에러(예: 자료형 불일치)가 발생한 경우 이번 배치만 실패로 기록, 다음으로 넘어간다.
            total_failed += len(chunk)
            print(f'{i+1}번째 배치 실패(이 배치만 롤백, 다음 배치 계속 진행): {e}')

    # 최종 결과를 딕셔너리로 정리 (다른 모듈에서 결과를 활용할 수 있도록 반환)
    summary = {
        "success": total_success,
        "skipped_duplicate": total_skipped,
        "failed": total_failed,
    }
    print (
        f'[loader] 전체 적재 완료 신규: {total_success:,}건'
        f'/ 중복스킵: {total_skipped:,}건'
        f'/ 실패: {total_failed:,}건'
    )
    return summary


# 이 파일을 직접 실행 했을 때만 (python loader.py) 아래 코드가 동작한다.
# 다른 모듈(파일)에서 import loader만 했을 때는 이 부분이 실행되지 않는다. 

if __name__== '__main__':
    load_from_csv()