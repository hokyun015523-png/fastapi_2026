# 빅데이터 저장 시스템 개발 - NCS
- 빅데이터 저장모델 설계
- 빅데이터 적재모듈 개발

---
## 대구 버스 노선 데이터 저장 시스템 실습

| 파일명 | 설명
|---|---|
| `models.py` | SQLAlchemy 테이블 모델 정의 |
| `database.py` | DB연결과 테이블 생성 |
| `loader.py` | CSV 적재 |
| `verify.py` | 검증. 대상 테이블을 정확히 조사 |
| `pipeline.py` | 통합 실행 |
| `README.md` | 실행 방법과 설계 설명 |
| `bus_nb.ipynb` | 셀 단위로 실습 (가장 먼저 실습)

---

### pgAdmin에서 데이터 베이스 준비
```sql
CREATE DATABASE busapidb;
```
---

### 입력 파일 준비

| 폴더 | 필요한 파일 |
| --- | --- |
| `fastapi/storage_subway_busapi/02_bus/input/` | `bus_stop.csv` |

---

- 결과로 나온 파일 `bus_stop.csv` 를 사용한다.
- CSV 인코딩은 `utf-8-sing` 기준

---
