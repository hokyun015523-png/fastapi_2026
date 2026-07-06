#===========================================================
# storage_subway_busapi/01sybway/models.py
# 
# 저장 모델 설계 (스키마)
#   기본키 + UNIQUE 제약 조건 추가
#
# 직접 실행되는 파일은 아니다. 
#   database.py, loader.py가 import해서 사용
#===========================================================

# 라이브러리 불러오기
from sqlalchemy import Column, Integer, String, Date, Boolean, UniqueConstraint
from sqlalchemy.orm import declarative_base

# 모든 모델 클래스가 상속받을 선언적 베이스 클래스를 생성
# 이 Base를 상속 받으면 클래스 = 테이블, 클래스 속성 = 컬럼으로 자동 매핑
Base = declarative_base()

class SubwayRaw(Base):
    # 실제 PostgreSQL에 생성될 테이블 이름
    __tablename__ = 'subway_raw'

    # 대체키(surrogate key):  비즈니스 의미가 없는 순수 일련번호 기본키(PK)
    # id를 기본키로 정했다 -> 고유값이 없어서
    id = Column(Integer, primary_key=True, autoincrement=True)

    # 실제 데이터 컬럼들 (모두 필수값--> nullable=False)
    월 = Column(Integer, nullable=False)  # 승하차가 발생한 월(1~12)
    일 = Column(Integer, nullable=False)  # 승하차가 발생한 일(1~31)
    역번호 = Column(Integer, nullable=False)  # 지하철역 고유번호
    역명 = Column(String(50), nullable=False) # 역 이름(예: '반월당')
    승하차 = Column(String(10), nullable=False)  # '승차' 또는 '하차' 
    시간대컬럼 = Column(String(20), nullable=False)  # 원본 csv의 시간대 컬럼명('05시-06시')
    인원수 = Column(Integer, nullable=False) # 해당 시간대의 승하차 인원 수
    시작시 = Column(Integer, nullable=False) # 시간대컬럼에서 뽑아낸 시작 시각 (0~23) -> 시간대별 집계/정렬 사용
    날짜 = Column(Date, nullable=False)  # 연-월-일이 합쳐진 실제 날짜 타입
    요일코드 = Column(String(5), nullable=False)  # 요일 표시 (예: '월', '화'...)
    주말여부 = Column(Boolean, nullable=False)  # 주말(토/일) 여부 --> True / False

    # 복합 UNIQUE 제약 조건 --> "같은 역 + 같은 날짜 + 같은 시간대 + 같은 승/하차" --> 1개만
    __table_args__ = (
        UniqueConstraint('역번호', '날짜', '시간대컬럼', '승하차', name='uq_subway_raw_key'),
    )

    def __repr__(self):
        """
        이 메서드를 정의해두면,  print(객체) 또는 터미널에서 객체를 
        그냥 출력했을때 사람이 읽기 쉬운 문자열 형태로 보여준다. 
        보통은 메모리 주소만 나오는데 __repr__을 만들어주면
        디버깅 할 때 어떤 데이터인지 알아보기 쉬워진다.
        """
        return f'<SubwayRaw {self.역명} {self.날짜} {self.시간대컬럼} {self.승하차}={self.인원수}>'

