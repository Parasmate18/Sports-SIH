import oracledb

from app.db.connection import get_connection
from app.core.security import hash_password
from app.schemas.auth import RegisterRequest
from app.core.security import verify_password, create_access_token


def register_user(data: RegisterRequest) -> dict:
    connection = None
    cursor = None

    try:
        connection = get_connection()
        cursor = connection.cursor()

        out_status = cursor.var(str, size=50)
        out_message = cursor.var(str, size=4000)

        hashed_password = hash_password(data.password)

        cursor.callproc(
            "USER_MANAGEMENT.INSERT_USER_DETAILS",
            [
                data.role,
                data.first_name,
                data.last_name,
                int(data.mobile_number),
                data.age,
                data.gender,
                data.username,
                hashed_password,
                data.address_line_1,  # P_ADDR_LINE_1
                data.district,        # P_DIST
                data.postal_code,     # P_PSTL_CD
                data.state,           # P_STATE
                data.country or "INDIA",  # P_COUNTRY
                data.weight_kg,       # P_WGT
                data.height_cm,       # P_HGT
                out_status,
                out_message,
            ],
        )

        status = out_status.getvalue()
        message = out_message.getvalue()

        if status == "SUCCESS":
            connection.commit()
        else:
            connection.rollback()

        return {
            "status": status,
            "message": message,
        }

    except oracledb.DatabaseError:
        if connection:
            connection.rollback()
        raise

    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()





def login_user(username: str, password: str) -> dict | None:
    connection = None
    cursor = None

    try:
        connection = get_connection()
        cursor = connection.cursor()

        cursor.execute(
            """
            SELECT USERID, USERNAME, PASSWORD, ROLE
            FROM USER_DETAILS
            WHERE UPPER(USERNAME) = UPPER(:username)
            """,
            {"username": username},
        )

        row = cursor.fetchone()

        if row is None:
            return None

        user_id, db_username, hashed_password, role = row

        if not verify_password(password, hashed_password):
            return None

        token = create_access_token(
            user_id=user_id,
            username=db_username,
            role=role,
        )

        return {
            "access_token": token,
            "token_type": "bearer",
            "user_id": user_id,
            "username": db_username,
            "role": role,
        }

    finally:
        if cursor:
            cursor.close()

        if connection:
            connection.close()            