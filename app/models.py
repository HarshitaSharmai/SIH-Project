from sqlalchemy import Column, Integer, String
from app.db import Base

class Terminology(Base):
    __tablename__ = "terminology"

    id = Column(Integer, primary_key=True, index=True)
    namaste_code = Column(String, unique=True, index=True, nullable=False)
    disorder_name = Column(String, index=True, nullable=False)
    icd11_tm2_code = Column(String, index=True, nullable=True)
    icd11_biomedicine_code = Column(String, index=True, nullable=True)
    who_ayurveda_term = Column(String, index=True, nullable=True)
