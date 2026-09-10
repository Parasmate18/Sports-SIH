from app.db.connection import get_connection


def save_cv_result(
    assessment_id: int,
    user_id: int,
    result: dict,
) -> int:

    connection = None
    cursor = None

    try:
        connection = get_connection()
        cursor = connection.cursor()

        # ==================================================
        # 1. Verify assessment ownership
        # ==================================================

        cursor.execute(
            """
            SELECT
                USER_ID,
                STATUS
            FROM ASSESSMENTS
            WHERE ASSESSMENT_ID = :assessment_id
            """,
            {
                "assessment_id": assessment_id
            },
        )

        assessment = cursor.fetchone()

        if assessment is None:
            raise ValueError(
                "Assessment not found"
            )

        assessment_user_id = int(
            assessment[0]
        )

        assessment_status = str(
            assessment[1]
        )

        if assessment_user_id != user_id:
            raise ValueError(
                "Assessment does not belong to current athlete"
            )

        if assessment_status == "COMPLETED":
            raise ValueError(
                "Assessment is already completed"
            )

        # ==================================================
        # 2. Map CV status to existing DB status
        # ==================================================

        cv_status = str(
            result.get(
                "status",
                "INCOMPLETE",
            )
        ).upper()

        if cv_status == "SUCCESS":
            db_status = "SUCCESS"
        else:
            db_status = "FAILED"

        quality = result.get(
            "quality",
            {}
        ) or {}

        # ==================================================
        # 3. Insert CV session
        # ==================================================

        new_session_id = cursor.var(
            int
        )

        cursor.execute(
            """
            INSERT INTO CV_SESSION_RESULTS
            (
                TEST_NAME,
                STATUS,
                INPUT_SOURCE,
                PERSON_DETECTED,
                FRAMES_PROCESSED,
                PERSON_FRAMES,
                INVALID_FRAMES,
                LAST_STAGE,
                LAST_FRAME_VALID_POSTURE,
                VALID_REPS
            )
            VALUES
            (
                :test_name,
                :status,
                :input_source,
                :person_detected,
                :frames_processed,
                :person_frames,
                :invalid_frames,
                :last_stage,
                :last_frame_valid_posture,
                :valid_reps
            )
            RETURNING SESSION_ID
            INTO :new_session_id
            """,
            {
                "test_name":
                    result.get("test"),

                "status":
                    db_status,

                "input_source":
                    result.get(
                        "input_source",
                        "video",
                    ),

                "person_detected":
                    1
                    if result.get(
                        "person_detected",
                        False,
                    )
                    else 0,

                "frames_processed":
                    result.get(
                        "frames_processed",
                        0,
                    ),

                "person_frames":
                    result.get(
                        "person_frames",
                        0,
                    ),

                "invalid_frames":
                    quality.get(
                        "invalid_frames",
                        0,
                    ),

                "last_stage":
                    quality.get(
                        "last_stage"
                    ),

                "last_frame_valid_posture":
                    1
                    if quality.get(
                        "last_frame_valid_posture",
                        False,
                    )
                    else 0,

                "valid_reps":
                    result.get(
                        "valid_reps",
                        0,
                    ),

                "new_session_id":
                    new_session_id,
            },
        )

        session_id = int(
            new_session_id.getvalue()[0]
        )

        # ==================================================
        # 4. Link session to assessment
        # ==================================================

        cursor.execute(
            """
            INSERT INTO ASSESSMENT_CV_LINK
            (
                ASSESSMENT_ID,
                SESSION_ID
            )
            VALUES
            (
                :assessment_id,
                :session_id
            )
            """,
            {
                "assessment_id":
                    assessment_id,

                "session_id":
                    session_id,
            },
        )

        # ==================================================
        # 5. Save measurement
        # ==================================================

        measurement = result.get(
            "measurement",
            {}
        ) or {}

        for feature_name, feature_value in measurement.items():

            if feature_value is None:
                continue

            cursor.execute(
                """
                INSERT INTO CV_MEASUREMENTS
                (
                    SESSION_ID,
                    FEATURE_NAME,
                    FEATURE_VALUE
                )
                VALUES
                (
                    :session_id,
                    :feature_name,
                    :feature_value
                )
                """,
                {
                    "session_id":
                        session_id,

                    "feature_name":
                        feature_name,

                    "feature_value":
                        float(feature_value),
                },
            )

        # ==================================================
        # 6. Save supported CV feature metrics
        # ==================================================

        features = result.get(
            "features",
            {}
        ) or {}

        feature_columns = {
            "elbow_angle":
                features.get(
                    "elbow_angle"
                ),

            "body_angle":
                features.get(
                    "body_angle"
                ),

            "body_horizontal_angle":
                features.get(
                    "body_horizontal_angle"
                ),

            "knee_angle":
                features.get(
                    "knee_angle"
                ),

            "torso_lean":
                features.get(
                    "torso_lean"
                ),
        }

        if any(
            value is not None
            for value
            in feature_columns.values()
        ):

            cursor.execute(
                """
                INSERT INTO CV_FEATURE_METRICS
                (
                    SESSION_ID,
                    ELBOW_ANGLE,
                    BODY_ANGLE,
                    BODY_HORIZONTAL_ANGLE,
                    KNEE_ANGLE,
                    TORSO_LEAN
                )
                VALUES
                (
                    :session_id,
                    :elbow_angle,
                    :body_angle,
                    :body_horizontal_angle,
                    :knee_angle,
                    :torso_lean
                )
                """,
                {
                    "session_id":
                        session_id,

                    **feature_columns,
                },
            )

        # ==================================================
        # 7. Mark assessment IN_PROGRESS
        # ==================================================

        cursor.execute(
            """
            UPDATE ASSESSMENTS
            SET STATUS = 'IN_PROGRESS'
            WHERE ASSESSMENT_ID = :assessment_id
              AND STATUS = 'CREATED'
            """,
            {
                "assessment_id":
                    assessment_id
            },
        )

        connection.commit()

        return session_id

    except Exception:
        if connection:
            connection.rollback()

        raise

    finally:
        if cursor:
            cursor.close()

        if connection:
            connection.close()