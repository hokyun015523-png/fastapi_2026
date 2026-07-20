# NCS 빅데이터 처리 시스템 실습

## 의약품 연령금기 데이터 처리 시스템

저장시스템 실습에서 구축한 PostgreSQL 의약품 연령금기 데이터를 이용하여
배치 처리(Batch Processing), 이벤트 처리(Event Processing), 검증(Verify Processing) 실행.

---

### 1. 전제 조건

저장시스템이 생성되어 있어야 합니다.

| DB | 테이블 |
| --- | --- |
| `kids_age_db` | `drug_age` |

---

### 2. DB 접속 정보

config.py에서 PostgreSQL 접속 정보를 설정합니다.

---

### 3. 실행

전체 처리 실행

```bash
python pipeline.py
```

또는 개별 실행

```bash
python batch_processor.py

python event_processor.py

python verify_processing.py
```

---

### 4. 결과 테이블

| DB | 결과 테이블 |
| --- | --- |
| `kids_age_db` | `drug_insurance_summary` |
| `kids_age_db` | `drug_agegroup_summary` |
| `kids_age_db` | `drug_company_summary` |
| `kids_age_db` | `drug_event_alert` |

---

### 5. 확인 SQL

```sql
SELECT * FROM drug_insurance_summary;

SELECT * FROM drug_agegroup_summary;

SELECT * FROM drug_company_summary;

SELECT * FROM drug_event_alert;
```

---

### 6. 처리 과정

- **batch_processor.py**
  - 급여구분별 의약품 개수 집계
  - 금기연령층별 의약품 개수 집계
  - 업체별 의약품 개수 집계

- **event_processor.py**
  - 특정연령 기준값(Threshold)을 초과하는 의약품을 탐지
  - 이벤트 결과를 `drug_event_alert` 테이블에 저장

- **verify_processing.py**
  - 원본 및 결과 테이블의 건수를 확인하여 처리 결과를 검증

- **pipeline.py**
  - 배치 처리 → 이벤트 처리 → 결과 검증을 순서대로 실행

### 7. 프로젝트 구성
```
    09_NCS-drug
    ┣ __pycache__
    ┃ 
    ┣ batch_processor.py
    ┣ config.py
    ┣ database.py
    ┣ event_processor.py
    ┣ pipeline.py
    ┣ README.md
    ┗ verify_processing.py
    ```