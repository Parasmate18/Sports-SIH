from typing import Literal

from pydantic import BaseModel, Field


class AthleteProfileInput(BaseModel):
    age: int = Field(ge=5, le=100)
    gender: Literal["Male", "Female", "Other"]
    height_cm: float = Field(ge=80, le=250)
    weight_kg: float = Field(ge=20, le=300)