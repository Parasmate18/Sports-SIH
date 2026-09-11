from pydantic import BaseModel


class UserProfileResponse(BaseModel):
    user_id: int
    role: str
    first_name: str
    last_name: str
    mobile_number: int
    age: int
    gender: str

    address_line_1: str | None = None
    district: str | None = None
    postal_code: str | None = None
    state: str | None = None
    country: str | None = None

    username: str

    weight_kg: float | None = None
    height_cm: float | None = None