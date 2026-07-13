"""문제 1. 원본 데이터 탐색하기."""

from sqlalchemy import inspect, text

from database import subway_engine


def print_columns() -> None:
    """subway_raw의 컬럼명과 데이터 형식을 출력합니다."""
    columns = inspect(subway_engine).get_columns("subway_raw")

    print("\n[1] 컬럼명과 데이터 형식")

    for column in columns:
        print(f'{column["name"]}: {column["type"]}')


def execute_and_print(title: str, sql: str) -> None:
    """SQL을 실행하고 조회 결과를 출력합니다."""
    print(f"\n[{title}]")

    with subway_engine.connect() as conn:
        rows = conn.execute(text(sql)).fetchall()

    for row in rows:
        print(row)


def main() -> None:
    print_columns()

    execute_and_print(
        "2. 전체 행 수",
        """
        SELECT COUNT(*) AS total_rows
        FROM subway_raw
        """,
    )

    execute_and_print(
        "3. 지하철역 개수",
        """
        SELECT COUNT(DISTINCT "역번호") AS station_count
        FROM subway_raw
        """,
    )

    execute_and_print(
        "4. 승하차 구분의 종류",
        """
        SELECT DISTINCT "승하차" AS ride_type
        FROM subway_raw
        ORDER BY ride_type
        """,
    )

    execute_and_print(
        "5. 승하차 구분별 행 수",
        """
        SELECT
            "승하차" AS ride_type,
            COUNT(*) AS row_count
        FROM subway_raw
        GROUP BY "승하차"
        ORDER BY "승하차"
        """,
    )

    execute_and_print(
        "6. 인원 값이 가장 큰 데이터 10건",
        """
        SELECT *
        FROM subway_raw
        ORDER BY "인원수" DESC
        LIMIT 10
        """,
    )

    execute_and_print(
        "7. 조회 기간",
        """
        SELECT
            MIN("날짜") AS min_date,
            MAX("날짜") AS max_date
        FROM subway_raw
        """,
    )

    execute_and_print(
        "8. 인원 값이 NULL인 행 수",
        """
        SELECT COUNT(*) AS null_passenger_count
        FROM subway_raw
        WHERE "인원수" IS NULL
        """,
    )


if __name__ == "__main__":
    main()