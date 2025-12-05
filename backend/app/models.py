from sqlalchemy import Column, Integer, String, Float
from .database import Base

class University(Base):
    __tablename__ = "universities"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    city = Column(String, nullable=False)
    type = Column(String, nullable=False)  # private / state
    rating = Column(Float, default=0)
    students = Column(Integer)
    programs = Column(Integer)
    min_score = Column(Integer)  # минимальный проходной балл
    image = Column(String, nullable=True)
