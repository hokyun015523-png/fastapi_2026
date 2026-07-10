#===========================================================
#  drug_storage/verify.py
#===========================================================
from sqlalchemy import text as sa_text
from database import engine

AGE_GROUP_LIST = {'영유아', '소아', '청소년', '성인', '임부', '노인', '전연령층', '기타', '고령자'}

def verify():
    with engine.connect() as conn:
        total = conn.execute(sa_text("SELECT COUNT(*) FROM drug_age")).scalar()

        # 2. 필수 컬럼별 NULL 개수 동시 고속 집계
        null_check = conn.execute(sa_text("""
            SELECT COUNT(*) FILTER (WHERE 제품명 IS NULL) AS null_name,
                   COUNT(*) FILTER (WHERE 특정연령 IS NULL) AS null_age,
                   COUNT(*) FILTER (WHERE 금기연령층 IS NULL) AS null_group
            FROM drug_age
        """)).fetchone()

        out_of_range = conn.execute(sa_text("""
            SELECT COUNT(*) FROM drug_age
            WHERE 특정연령 < 0 OR 특정연령 > 150
        """)).scalar()

        group_values = conn.execute(sa_text(
            "SELECT DISTINCT 금기연령층 FROM drug_age"
        )).fetchall()
        
        invalid_group = []
        for g in group_values:
            if g[0] is not None and g[0] not in AGE_GROUP_LIST:
                invalid_group.append(g[0])

    print('==== 의약품 적재 검증 결과 ====')
    print(f'전체 건수 : {total:,}')
    print(f'제품명 NULL 건수 : {null_check[0]}')
    print(f'특정연령 NULL 건수 : {null_check[1]}')
    print(f'금기연령층 NULL 건수 : {null_check[2]}')
    print(f'특정연령 범위 이탈 건수 : {out_of_range}')
    print(f'금기연령층 이상값 : {invalid_group if invalid_group else "없음"}')

    ok = (null_check[0] == 0 and null_check[1] == 0 and null_check[2] == 0 
          and out_of_range == 0 and not invalid_group)
          
    print(f'검증결과 : {ok}')
    return ok

if __name__ == '__main__':
    verify()
