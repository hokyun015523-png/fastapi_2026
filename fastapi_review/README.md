# FastAPI 복습 - 공식 튜토리얼로 다시 다지는 FastAPI 핵심

## 실습 순서

| 단계 | 내용 |
|---|---|
| ① sql_databases | User + Item 두 데이블, 1:N 관리, crud.py 분리 |
| ② bigger_applications | routers /폴더 분리구조 |
| ③ app_testing | TestClient로 엔트포인트 자동 데스트 - pytest |

## 실습 환경
- `**python 3.11**`
- **패키지관리** : `uv`
- **DB** : `PostgreSQL 17`
    - DB명 : `reviewdb`
- **IDE** : `VS Code`
- **터미널** : `Git Bash`

## 1. sql_databases --> User + Item, 1:N관계 CRUD
- 공식 FastAPI 듀토리얼 예제를 PostgreSQL로 변환한 버전이다.
- `User`(사용자)가 여러개의 `Item` (아이템)을 소유하는 **1:N관계** 구조
- `crud.py` 를 별도로 분리하여 DB조작 로직과 라우터 로직을 나눈다.

```
fastapi_review
 ┣ routers
 ┃ ┣ __pycache__
 ┃ ┃ ┣ items.cpython-311.pyc
 ┃ ┃ ┣ users.cpython-311.pyc
 ┃ ┃ ┗ __init__.cpython-311.pyc
 ┃ ┣ items.py
 ┃ ┣ users.py
 ┃ ┗ __init__.py
 ┣ __pycache__
 ┃ ┣ crud.cpython-311.pyc
 ┃ ┣ database.cpython-311.pyc
 ┃ ┣ dependencies.cpython-311.pyc
 ┃ ┣ main.cpython-311.pyc
 ┃ ┣ models.cpython-311.pyc
 ┃ ┗ schemas.cpython-311.pyc
 ┣ crud.py
 ┣ database.py
 ┣ dependencies.py
 ┣ main.py
 ┣ models.py
 ┣ README.md
 ┗ schemas.py

```