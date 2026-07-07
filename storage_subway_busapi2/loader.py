# ================================================
# storage_subway_busapi/02_bus/loader.py
#
# 수집한 결과로 나온 파일 bus_stop.csv을
# 테이블에 적재
# ================================================
import os
import pandas as pd
from database import get_session
from models import BusStop


BASE_DIR = os.getcwd()
INPUT_PATH = os.path.join(BASE_DIR, 'input', 'bus_stop.csv')

def load_from_csv(path: str=INPUT_PATH) -> dict:
    df = pd.read_csv(path, encoding='utf-8-sig')
    df['수집일시'] = pd.to_datetime(df['수집일시'], errors='coerce').dt.date
    df['정류소번호'] = pd.to_numeric(df['정류소번호'], errors='coerce')

    db = get_session()
    success = 0
    failed = 0

    for _, row in df.iterrows():
        try:
            stop = BusStop(
                정류소ID = str(row['정류소ID']),
                정류소명 = str(row['정류소명']),
                # pd.notna() : NaN/None 여부 확인 후, 값이 있을 때만 형변환
                정류소번호 = int(row['정류소번호']) if pd.notna(row['정류소번호']) else None,
                위도 = float(row['위도']) if pd.notna(row['위도']) else None,
                경도 = float(row['경도']) if pd.notna(row['경도']) else None,
                수집일시 = row['수집일시'],
                위치구분 = str(row['위치구분']) if pd.notna(row['위치구분']) else None,
            )
            db.merge(stop)
            db.commit()
            success += 1
        except Exception as e:
            # 실패한 행만 롤백하고, 다음 행은 이어서 진행
            db.rollback()
            failed += 1
            print(f'적재 실패 - {row.get("정류소명")} / {e}')

    db.close()

    print(f'[loader] 적재 완료 - 성공: {success:,}건 / 실패: {failed:,}건')

    return {'success': success, 'failed': failed}
