from typing import Literal

from pydantic import BaseModel, Field, field_validator

class RegisterRequest(BaseModel):
    role: Literal["ATHLETE", "COACH", "SCOUT"]

    first_name: str = Field(min_length=1, max_length=50)
    last_name: str = Field(min_length=1, max_length=50)

    mobile_number: str = Field(pattern=r"^\d{10}$")
    age: int = Field(ge=5, le=100)
    gender: Literal["M", "F", "O"]

    address_line_1: str | None = Field(default=None, max_length=200)
    district: str | None = Field(default=None, max_length=100)
    postal_code: str | None = Field(default=None, pattern=r"^\d{6}$")
    state: str | None = Field(default=None, max_length=100)
    country: str | None = Field(default="INDIA", max_length=100)

    height_cm: float | None = Field(
        default=None,
        ge=80,
        le=250,
    )

    weight_kg: float | None = Field(
        default=None,
        ge=20,
        le=300,
    )

    username: str = Field(min_length=3, max_length=50)
    password: str = Field(min_length=8, max_length=128)

    @field_validator("username")
    @classmethod
    def clean_username(cls, value: str) -> str:
        return value.strip()



class RegisterResponse(BaseModel):
    status: str
    message: str


class LoginRequest(BaseModel):
    username: str
    password: str


class LoginResponse(BaseModel):
    access_token: str
    token_type: str
    user_id: int
    username: str
    role: str