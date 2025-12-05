from pydantic import BaseModel

class UniversityBase(BaseModel):
    name: str
    city: str
    type: str
    rating: float
    students: int
    programs: int
    min_score: int
    image: str | None = None

class UniversityCreate(UniversityBase):
    pass

class University(UniversityBase):
    id: int

    class Config:
        orm_mode = True
