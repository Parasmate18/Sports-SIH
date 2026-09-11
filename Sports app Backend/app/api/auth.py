import logging

import oracledb
from fastapi import APIRouter, HTTPException, status
from app.schemas.auth import RegisterRequest, RegisterResponse
from app.services.auth_service import register_user
from app.schemas.auth import (
    RegisterRequest,
    RegisterResponse,
    LoginRequest,
    LoginResponse,
)
from app.services.auth_service import (
    register_user,
    login_user,
)


router = APIRouter(prefix="/api/v1/auth", tags=["Authentication"])

logger = logging.getLogger(__name__)


@router.post(
    "/register",
    response_model=RegisterResponse,
    status_code=status.HTTP_201_CREATED,
)
def register(data: RegisterRequest):
    logger.info("Registration requested for username=%r", data.username)

    try:
        result = register_user(data)

        logger.info(
            "Registration result for username=%r: status=%r, message=%r",
            data.username,
            result.get("status"),
            result.get("message"),
        )

        if result["status"] != "SUCCESS":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Registration could not be completed. Check your details or try another username.",
            )

        return result

    except oracledb.DatabaseError:
        logger.exception("Database error during registration")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Registration service is temporarily unavailable.",
        )




@router.post(
    "/login",
    response_model=LoginResponse,
)
def login(data: LoginRequest):
    result = login_user(
        username=data.username,
        password=data.password,
    )

    if result is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
        )

    return result   