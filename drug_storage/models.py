#===========================================================
# drug_storage/models.py
#===========================================================
from sqlalchemy import Column, Integer, String, UniqueConstraint
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class DrugAgeContraindication(Base):
    __tablename__ = "drug_age"

    # 대체키(PK)
    id = Column(Integer, primary_key=True, autoincrement=True)

    # 제품명
    product_name = Column("제품명", String(255), nullable=False)

    # 급여구분
    insurance_type = Column("급여구분", String(20), nullable=False)

    # 특정연령
    specific_age = Column("특정연령", Integer, nullable=False)  

    # 특정연령단위
    age_unit = Column("특정연령단위", String(20), nullable=False)

    # 업체명
    company = Column("업체명", String(255), nullable=False)

    # 파생 컬럼
    age_group = Column("금기연령층", String(50), nullable=False)

    
    __table_args__ = (
        UniqueConstraint(
            "제품명", "특정연령", "특정연령단위", "업체명", 
            name="uq_drug_age"
        ),
    )

    def __repr__(self):
        return (
            f"<DrugAgeContraindication("f"제품명='{self.product_name}', "f"급여구분='{self.insurance_type}', "
            f"특정연령={self.specific_age}, "f"특정연령단위='{self.age_unit}', "f"업체명='{self.company}', "
            f"금기연령층='{self.age_group}')>"
        )