# 의약품 연령금기 데이터 저장 프로젝트

## 프로젝트 소개

식품의약품안전처(KIDS)의 의약품 연령금기 대량 데이터를 PostgreSQL 데이터베이스에 안정적으로 저장하는 프로젝트입니다.

대용량 CSV 파일을 안전하게 분할하여 데이터를 적재하고, 중복을 방어하며, 적재 결과를 교차 검증하는 전체 파이프라인 과정을 SQLAlchemy ORM 기법으로 구현하였습니다.

---

## 사용 데이터
- **데이터 출처** : https://www.data.go.kr/tcs/dss/selectFileDataDetailView.do?publicDataPk=15089531#tab-layer-file

- **데이터명** : KIDS 의약품 연령금기 정보
- **파일명** : KIDS_Age_Contraindications_final.csv

### 사용된 컬럼
- 제품명
- 급여구분
- 특정연령
- 특정연령단위
- 업체명
- 금기연령층 (파생 컬럼)

---

## 프로젝트 구성

```
drug_storage
 ┣ input
 ┃ ┗ KIDS_Age_Contraindications_final.csv
 ┣ __pycache__
 ┃ ┣ database.cpython-311.pyc
 ┃ ┣ loader.cpython-311.pyc
 ┃ ┣ models.cpython-311.pyc
 ┃ ┗ verify.cpython-311.pyc
 ┣ database.py
 ┣ dddd.ipynb
 ┣ loader.py
 ┣ models.py
 ┣ pipeline.py
 ┣ README.md
 ┗ verify.py
```

---

## 제약조건 설계 특징

### Unique 복합 제약조건
- **중복 판단 기준** : `(제품명, 특정연령, 특정연령단위, 업체명)`
- **설계 의도** : 공공데이터 특성상 동일한 약품 정보가 여러 번 수집될 수 있습니다. 위 4개 컬럼이 완전히 일치하는 중복 데이터가 들어올 경우, 데이터베이스가 스스로 판단하여 저장을 스킵하도록 안전장치를 설계했습니다.

---

## 파일 설명

### models.py
SQLAlchemy ORM을 이용하여 데이터베이스 테이블 구조를 정교하게 정의하였습니다.
- 자동 증가 기본키(`id`) 배치
- 필수 필수 필드 `NOT NULL` 제약조건 설정
- 중복 방지용 복합 `UNIQUE` 제약조건 탑재

### database.py
PostgreSQL 데이터베이스와의 연결 세션을 세팅하고 관리합니다.
- 프로그램 가동 시 테이블 방을 자동으로 개설해 주는 `init_db()` 내장

### loader.py
대용량 파일을 5,000건씩 청크 단위로 쪼개어 읽어 메모리 과부하를 막습니다.
- 중복 데이터 충돌 시 조용히 넘어가는 고속 업서트(`ON CONFLICT DO NOTHING`) 전략 적용

### verify.py
데이터 적재가 완전히 완료된 후, 유실(NULL)이나 연령 도메인 범위 이탈 등의 이상치가 없는지 최종 품질 점검을 수행하는 무결성 검증 센터입니다.

### pipeline.py
위의 모든 공정(구조 생성 / 고속 적재 / 교차 검증)을 총괄 지휘하여 원클릭으로 한 번에 가동해 주는 마스터 통합 파일입니다.
