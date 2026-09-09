from app.db.connection import get_connection
import json

REQUIRED_MEASUREMENTS = {
    "pushup_count",
    "squat_count",
    "deadlift_reps",
    "running_50m_seconds",
    "situp_count",
    "plank_duration_seconds",
    "vertical_jump_cm",
}


def create_assessment(user_id: int) -> dict:
    connection = None
    cursor = None

    try:
        connection = get_connection()
        cursor = connection.cursor()

        new_id = cursor.var(int)

        cursor.execute(
            """
            INSERT INTO ASSESSMENTS (USER_ID, STATUS)
            VALUES (:user_id, 'CREATED')
            RETURNING ASSESSMENT_ID INTO :new_id
            """,
            {
                "user_id": user_id,
                "new_id": new_id,
            },
        )

        assessment_id = new_id.getvalue()[0]

        cursor.execute(
            """
            SELECT
                ASSESSMENT_ID,
                USER_ID,
                STATUS,
                CREATED_AT,
                COMPLETED_AT
            FROM ASSESSMENTS
            WHERE ASSESSMENT_ID = :assessment_id
            """,
            {"assessment_id": assessment_id},
        )

        row = cursor.fetchone()

        connection.commit()

        return {
            "assessment_id": row[0],
            "user_id": row[1],
            "status": row[2],
            "created_at": row[3],
            "completed_at": row[4],
        }

    except Exception:
        if connection:
            connection.rollback()
        raise

    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()


def get_m1_features_for_assessment(
    assessment_id: int,
    user_id: int,
    profile: dict,
) -> dict:
    connection = None
    cursor = None

    try:
        connection = get_connection()
        cursor = connection.cursor()

        # -------------------------------------------------
        # 1. Verify assessment exists and belongs to user
        # -------------------------------------------------
        cursor.execute(
            """
            SELECT USER_ID, STATUS
            FROM ASSESSMENTS
            WHERE ASSESSMENT_ID = :assessment_id
            """,
            {
                "assessment_id": assessment_id,
            },
        )

        assessment_row = cursor.fetchone()

        if not assessment_row:
            raise ValueError("Assessment not found.")

        assessment_user_id = assessment_row[0]

        if int(assessment_user_id) != int(user_id):
            raise PermissionError(
                "You are not allowed to access this assessment."
            )

        # -------------------------------------------------
        # 2. Get latest successful CV measurements
        # -------------------------------------------------
        cursor.execute(
            """
            WITH ranked_results AS (
                SELECT
                    CSR.SESSION_ID,
                    CM.FEATURE_NAME,
                    CM.FEATURE_VALUE,

                    ROW_NUMBER() OVER (
                        PARTITION BY CM.FEATURE_NAME
                        ORDER BY CSR.SESSION_ID DESC
                    ) AS rn

                FROM ASSESSMENT_CV_LINK ACL

                JOIN CV_SESSION_RESULTS CSR
                    ON CSR.SESSION_ID = ACL.SESSION_ID

                JOIN CV_MEASUREMENTS CM
                    ON CM.SESSION_ID = CSR.SESSION_ID

                WHERE ACL.ASSESSMENT_ID = :assessment_id
                  AND CSR.STATUS = 'SUCCESS'
                  AND CM.FEATURE_VALUE IS NOT NULL
            )

            SELECT
                FEATURE_NAME,
                FEATURE_VALUE
            FROM ranked_results
            WHERE rn = 1
            """,
            {
                "assessment_id": assessment_id,
            },
        )

        measurement_rows = cursor.fetchall()

        measurements = {}

        for feature_name, feature_value in measurement_rows:
            measurements[feature_name] = float(feature_value)

        # -------------------------------------------------
        # 3. Verify all 7 CV measurements exist
        # -------------------------------------------------
        missing_features = (
            REQUIRED_MEASUREMENTS - measurements.keys()
        )

        if missing_features:
            missing_list = ", ".join(
                sorted(missing_features)
            )

            raise ValueError(
                f"Assessment is incomplete. "
                f"Missing measurements: {missing_list}"
            )

        # -------------------------------------------------
        # 4. Validate frontend profile
        # -------------------------------------------------
        required_profile_fields = {
            "age",
            "gender",
            "height_cm",
            "weight_kg",
        }

        missing_profile_fields = (
            required_profile_fields - profile.keys()
        )

        if missing_profile_fields:
            missing_list = ", ".join(
                sorted(missing_profile_fields)
            )

            raise ValueError(
                f"Missing athlete profile fields: {missing_list}"
            )

        # -------------------------------------------------
        # 5. Normalize gender
        # -------------------------------------------------
        gender_text = str(
            profile["gender"]
        ).strip().upper()

        gender_map = {
            "M": "Male",
            "MALE": "Male",
            "F": "Female",
            "FEMALE": "Female",
            "O": "Other",
            "OTHER": "Other",
        }

        if gender_text not in gender_map:
            raise ValueError(
                "Gender must be Male, Female, or Other."
            )

        normalized_gender = gender_map[gender_text]

        # -------------------------------------------------
        # 6. Construct complete 11-feature M1 input
        # -------------------------------------------------
        features = {
            "age": int(profile["age"]),
            "gender": normalized_gender,
            "height_cm": float(profile["height_cm"]),
            "weight_kg": float(profile["weight_kg"]),

            "pushup_count": int(
                measurements["pushup_count"]
            ),

            "squat_count": int(
                measurements["squat_count"]
            ),

            "deadlift_reps": int(
                measurements["deadlift_reps"]
            ),

            "running_50m_seconds": float(
                measurements["running_50m_seconds"]
            ),

            "situp_count": int(
                measurements["situp_count"]
            ),

            "plank_duration_seconds": float(
                measurements["plank_duration_seconds"]
            ),

            "vertical_jump_cm": float(
                measurements["vertical_jump_cm"]
            ),
        }

        return features

    finally:
        if cursor:
            cursor.close()

        if connection:
            connection.close()

def save_final_prediction(
    assessment_id: int,
    user_id: int,
    features: dict,
    prediction: dict,
) -> dict:
    connection = None
    cursor = None

    try:
        connection = get_connection()
        cursor = connection.cursor()

        # -------------------------------------------------
        # 1. Verify assessment ownership + current status
        # -------------------------------------------------
        cursor.execute(
            """
            SELECT USER_ID, STATUS
            FROM ASSESSMENTS
            WHERE ASSESSMENT_ID = :assessment_id
            FOR UPDATE
            """,
            {
                "assessment_id": assessment_id,
            },
        )

        row = cursor.fetchone()

        if row is None:
            raise ValueError("Assessment not found.")

        assessment_user_id = int(row[0])
        assessment_status = str(row[1]).upper()

        if assessment_user_id != int(user_id):
            raise PermissionError(
                "You are not allowed to finalize this assessment."
            )

        if assessment_status == "COMPLETED":
            raise ValueError(
                "Assessment has already been completed."
            )

        # -------------------------------------------------
        # 2. Save exact 11 features used by M1
        # -------------------------------------------------
        cursor.execute(
            """
            INSERT INTO ASSESSMENT_FEATURE_SNAPSHOT (
                ASSESSMENT_ID,
                AGE,
                GENDER,
                HEIGHT_CM,
                WEIGHT_KG,
                PUSHUP_COUNT,
                SQUAT_COUNT,
                DEADLIFT_REPS,
                RUNNING_50M_SECONDS,
                SITUP_COUNT,
                PLANK_DURATION_SECONDS,
                VERTICAL_JUMP_CM
            )
            VALUES (
                :assessment_id,
                :age,
                :gender,
                :height_cm,
                :weight_kg,
                :pushup_count,
                :squat_count,
                :deadlift_reps,
                :running_50m_seconds,
                :situp_count,
                :plank_duration_seconds,
                :vertical_jump_cm
            )
            """,
            {
                "assessment_id": assessment_id,
                "age": features["age"],
                "gender": features["gender"],
                "height_cm": features["height_cm"],
                "weight_kg": features["weight_kg"],
                "pushup_count": features["pushup_count"],
                "squat_count": features["squat_count"],
                "deadlift_reps": features["deadlift_reps"],
                "running_50m_seconds":
                    features["running_50m_seconds"],
                "situp_count": features["situp_count"],
                "plank_duration_seconds":
                    features["plank_duration_seconds"],
                "vertical_jump_cm":
                    features["vertical_jump_cm"],
            },
        )

        # -------------------------------------------------
        # 3. Save M1 prediction
        # -------------------------------------------------
        strengths_json = json.dumps(
            prediction.get("strengths", [])
        )

        needs_json = json.dumps(
            prediction.get("needs_improvement", [])
        )

        cursor.execute(
            """
            INSERT INTO ASSESSMENT_PREDICTIONS (
                ASSESSMENT_ID,
                TALENT_LEVEL,
                CONFIDENCE,
                RECOMMENDED_SPORT,
                STRENGTHS,
                NEEDS_IMPROVEMENT,
                MODEL_VERSION
            )
            VALUES (
                :assessment_id,
                :talent_level,
                :confidence,
                :recommended_sport,
                :strengths,
                :needs_improvement,
                :model_version
            )
            """,
            {
                "assessment_id": assessment_id,
                "talent_level":
                    prediction["talent_level"],
                "confidence":
                    prediction["confidence"],
                "recommended_sport":
                    prediction["recommended_sport"],
                "strengths": strengths_json,
                "needs_improvement": needs_json,
                "model_version":
                    prediction["model_version"],
            },
        )

        # -------------------------------------------------
        # 4. Mark assessment completed
        # -------------------------------------------------
        cursor.execute(
            """
            UPDATE ASSESSMENTS
            SET
                STATUS = 'COMPLETED',
                COMPLETED_AT = CURRENT_TIMESTAMP
            WHERE ASSESSMENT_ID = :assessment_id
            """,
            {
                "assessment_id": assessment_id,
            },
        )

        connection.commit()

        return {
            "assessment_id": assessment_id,
            "status": "COMPLETED",
            "features": features,
            "prediction": prediction,
        }

    except Exception:
        if connection:
            connection.rollback()

        raise

    finally:
        if cursor:
            cursor.close()

        if connection:
            connection.close()            