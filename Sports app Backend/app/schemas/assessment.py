from datetime import datetime

from pydantic import BaseModel


class AssessmentResponse(BaseModel):
    assessment_id: int
    user_id: int
    status: str
    created_at: datetime
    completed_at: datetime | None = None


class ExerciseResultResponse(BaseModel):
    assessment_id: int
    session_id: int
    exercise: str
    status: str
    valid_reps: int
    measurement: dict
    features: dict
    quality: dict    