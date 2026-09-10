from app.db.connection import get_connection


def get_user_by_id(user_id: int) -> dict | None:
    connection = None
    cursor = None

    try:
        connection = get_connection()
        cursor = connection.cursor()

        cursor.execute(
            """
            SELECT
                USERID,
                ROLE,
                FNM,
                LNM,
                MOB_NO,
                AGE,
                GENDER,
                ADDR_LINE_1,
                DIST,
                PSTL_CD,
                STATE,
                COUNTRY,
                USERNAME,
                WGT,
                HGT
            FROM USER_DETAILS
            WHERE USERID = :user_id
            """,
            {"user_id": user_id},
        )

        row = cursor.fetchone()

        if row is None:
            return None

        return {
            "user_id": row[0],
            "role": row[1],
            "first_name": row[2],
            "last_name": row[3],
            "mobile_number": row[4],
            "age": row[5],
            "gender": row[6],
            "address_line_1": row[7],
            "district": row[8],
            "postal_code": row[9],
            "state": row[10],
            "country": row[11],
            "username": row[12],
            "weight_kg": row[13],
            "height_cm": row[14],
        }

    finally:
        if cursor:
            cursor.close()

        if connection:
            connection.close()