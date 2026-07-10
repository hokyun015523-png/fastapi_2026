#===========================================================
#  drug_storage/pipeline.py
#=========================================================
from database import init_db
from loader import load_from_csv
from verify import verify


def main():

    print("="*60)
    print("1) 저장 구조 생성")
    print("="*60)

    init_db()

    print()

    print("="*60)
    print("2) CSV 데이터 적재")
    print("="*60)

    load_from_csv()

    print()

    print("="*60)
    print("3) 데이터 검증")
    print("="*60)

    verify()


if __name__ == "__main__":
    main()