#===========================================================
# # drug_storage/loader.py
#===========================================================
import os
import pandas as pd

from sqlalchemy.dialects.postgresql import insert

from database import engine
from models import DrugAgeContraindication

BASE_DIR = os.getcwd()

INPUT_PATH = os.path.join(
    BASE_DIR,
    "input",
    "KIDS_Age_Contraindications_final.csv"
)

CHUNK_SIZE = 5000


def prepare_chunk(chunk):

    chunk = chunk.copy()

    chunk = chunk.dropna(
        subset=[
            "제품명",
            "급여구분",
            "특정연령",
            "특정연령단위",
            "업체명",
            "금기연령층"
        ]
    )

    chunk["특정연령"] = (
        pd.to_numeric(
            chunk["특정연령"],
            errors="coerce"
        )
        .fillna(0)
        .astype(int)
    )

    records = []

    for _, row in chunk.iterrows():

        records.append({

            "제품명": row["제품명"],
            "급여구분": row["급여구분"],
            "특정연령": int(row["특정연령"]),
            "특정연령단위": row["특정연령단위"],
            "업체명": row["업체명"],
            "금기연령층": row["금기연령층"]

        })

    return records


def load_from_csv():

    print("[Loader] 의약품 데이터 적재 시작")

    total_success = 0
    total_skip = 0
    total_fail = 0

    for idx, chunk in enumerate(

        pd.read_csv(
            INPUT_PATH,
            encoding="utf-8-sig",
            chunksize=CHUNK_SIZE
        )

    ):

        try:

            records = prepare_chunk(chunk)

            stmt = insert(
                DrugAgeContraindication.__table__
            )

            stmt = stmt.values(records)

            stmt = stmt.on_conflict_do_nothing(
                constraint="uq_drug_age"
            )

            with engine.begin() as conn:

                result = conn.execute(stmt)

            inserted = result.rowcount or 0

            skipped = len(records) - inserted

            total_success += inserted
            total_skip += skipped

            print(
                f"[{idx+1}번째 배치] "
                f"신규 {inserted:,}건 "
                f"/ 중복 {skipped:,}건"
            )

        except Exception as e:

            total_fail += len(chunk)

            print(f"[{idx+1}번째 배치 실패] {e}")

    print("=" * 70)
    print("의약품 적재 완료")
    print("=" * 70)
    print(f"신규 적재 : {total_success:,}")
    print(f"중복 제외 : {total_skip:,}")
    print(f"실패 : {total_fail:,}")
    print("=" * 70)


if __name__ == "__main__":
    load_from_csv()