# NCS 빅데이터 처리 시스템 실습

## 대구 교통 데이터 처리시스템 예제
저장시스템 실습에서 만든 PostgreSQL 테이블을 이용하여 배치 처리, 실시간 처리, 이벤트 처리 모듈을 실행하는 예제

### 1. 전제 조건
지난 주 저장시스템 실습이 완료되어 있어야 한다.

| DB | 테이블 |
| --- | --- |
| `subwaydb` | `subway_raw` |
| `busapidb` | `bus_stop` |


### 2. 필요한 라이브러리
```bash
uv add sqlalchemy psycopg2-binary
```

### 3. 환경변수
기본값은 저장시스템 실습과 같은 비밀번호 `1234`

```bash
set SUBWAY_DB_URL=postgresql://postgres:1234@localhost:5432/subwaydb
set BUS_DB_URL=postgresql://postgres:1234@localhost:5432/busapidb
```

### 4. 실행

```bash
python pipeline.py
```

### 5. 결과 테이블

| DB | 결과 테이블 |
| --- | --- |
| `subwaydb` | `traffic_subway_hourly_summary` |
| `subwaydb` | `traffic_realtime_window_summary` |
| `subwaydb` | `traffic_subway_event_alerts` |
| `busapidb` | `traffic_bus_area_summary` |
| `busapidb` | `traffic_bus_event_alerts` |

### 6. 확인 SQL

```sql
SELECT * FROM traffic_subway_hourly_summary ORDER BY total_passengers DESC LIMIT 20;
SELECT * FROM traffic_realtime_window_summary ORDER BY processed_at DESC LIMIT 20;
SELECT * FROM traffic_subway_event_alerts ORDER BY detected_at DESC LIMIT 20;   
```

```sql
SELECT * FROM traffic_bus_area_summary ORDER BY stop_count DESC;
SELECT * FROM traffic_bus_event_alerts ORDER BY detected_at DESC LIMIT 20;
```

### 7. 실습 목표
- 저장시스템은 데이터를 안전하게 저장하는 것이 목표
- 처리시스템은 저장된 데이터를 목적에 맞게 가공하여 새로운 결과를 만드는 것이 목표!

- Spark / Kafka 설치 없이 Python과 PostgreSQL로 처리 로직을 먼저 구현해서 이해!
- 같은 로직을 Spart SQL, Kafka, Flink, Esper, Hadoop, Hive 등 같은 도구로 확장할 수 있다.