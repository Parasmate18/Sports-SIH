import os
import tempfile
import math

from fastapi import (
    APIRouter,
    Depends,
    File,
    Form,
    HTTPException,
    UploadFile,
    status,
)

from ml.predict import predict_talent
from app.schemas.athlete_profile import AthleteProfileInput
from app.api.dependencies import get_current_user
from app.db.connection import get_connection
from app.integrations.cv_video_runner import process_exercise_video
from app.schemas.assessment import (
    AssessmentResponse,
    ExerciseResultResponse,
)
from app.services.assessment_service import (
    create_assessment,
    get_m1_features_for_assessment,
    save_final_prediction,
)
from app.services.cv_service import save_cv_result


router = APIRouter(
    prefix="/api/v1/assessments",
    tags=["Assessments"],
)

SUPPORTED_EXERCISES = {
    "pushup",
    "squat",
    "deadlift",
    "running",
    "situp",
    "plank",
    "vertical_jump",
}

ALLOWED_VIDEO_EXTENSIONS = {
    ".mp4",
    ".mov",
    ".avi",
    ".mkv",
}


# ==========================================================
# Helper: Get athlete height from USER_DETAILS
# ==========================================================

def get_athlete_height_cm(user_id: int):
    connection = None
    cursor = None

    try:
        connection = get_connection()
        cursor = connection.cursor()

        cursor.execute(
            """
            SELECT HGT
            FROM USER_DETAILS
            WHERE USERID = :user_id
            """,
            {"user_id": user_id},
        )

        row = cursor.fetchone()

        if row is None or row[0] is None:
            return None

        return float(row[0])

    finally:
        if cursor:
            cursor.close()

        if connection:
            connection.close()


# ==========================================================
# Helper: Get recommended coaches by athlete talent level
# ==========================================================

def get_recommended_coaches(cursor, talent_level: str):
    if not talent_level:
        return []

    normalized_level = talent_level.strip().upper()

    cursor.execute(
        """
        SELECT
            ID,
            USER_ID,
            NAME,
            PHONE,
            EMAIL,
            ORGANIZATION,
            CERTIFICATION_LEVEL,
            EXPERIENCE_YEARS,
            STATE,
            DISTRICT,
            TARGET_LEVEL
        FROM SYSTEM.COACHES
        WHERE UPPER(TARGET_LEVEL) = :talent_level
        ORDER BY EXPERIENCE_YEARS DESC, NAME ASC
        FETCH FIRST 3 ROWS ONLY
        """,
        {
            "talent_level": normalized_level
        },
    )

    rows = cursor.fetchall()

    coaches = []

    for row in rows:
        coaches.append(
            {
                "id": row[0],
                "user_id": row[1],
                "name": row[2],
                "phone": row[3],
                "email": row[4],
                "organization": row[5],
                "certification_level": row[6],
                "experience_years": (
                    int(row[7])
                    if row[7] is not None
                    else 0
                ),
                "state": row[8],
                "district": row[9],
                "target_level": row[10],
            }
        )

    return coaches


# ==========================================================
# CREATE NEW ASSESSMENT
# ==========================================================

@router.post(
    "",
    response_model=AssessmentResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_new_assessment(
    current_user: dict = Depends(get_current_user),
):
    if current_user["role"].upper() != "ATHLETE":
        raise HTTPException(
            status_code=403,
            detail="Only athletes can create assessments",
        )

    try:
        assessment = create_assessment(
            current_user["user_id"]
        )

        return assessment

    except Exception:
        raise HTTPException(
            status_code=500,
            detail="Could not create assessment",
        )


# ==========================================================
# GET COMPLETE M1 FEATURE INPUT
# TEMPORARY TEST ENDPOINT
# ==========================================================

@router.post("/{assessment_id}/features")
def get_assessment_features(
    assessment_id: int,
    profile: AthleteProfileInput,
    current_user: dict = Depends(get_current_user),
):
    if current_user["role"].upper() != "ATHLETE":
        raise HTTPException(
            status_code=403,
            detail="Only athletes can access assessment features",
        )

    try:
        features = get_m1_features_for_assessment(
            assessment_id=assessment_id,
            user_id=current_user["user_id"],
            profile=profile.model_dump(),
        )

        return {
            "assessment_id": assessment_id,
            "features": features,
        }

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        )

    except Exception as exc:
        print(f"Feature collection error: {exc}")

        raise HTTPException(
            status_code=500,
            detail="Could not collect assessment features",
        )


# ==========================================================
# PREDICT ASSESSMENT
# ==========================================================

@router.post("/{assessment_id}/predict")
def predict_assessment(
    assessment_id: int,
    profile: AthleteProfileInput,
    current_user: dict = Depends(get_current_user),
):
    if current_user["role"].upper() != "ATHLETE":
        raise HTTPException(
            status_code=403,
            detail="Only athletes can generate predictions",
        )

    try:
        features = get_m1_features_for_assessment(
            assessment_id=assessment_id,
            user_id=current_user["user_id"],
            profile=profile.model_dump(),
        )

        prediction = predict_talent(features)

        return {
            "assessment_id": assessment_id,
            "features": features,
            "prediction": prediction,
        }

    except PermissionError as exc:
        raise HTTPException(
            status_code=403,
            detail=str(exc),
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        )

    except FileNotFoundError as exc:
        print(f"M1 model file error: {exc}")

        raise HTTPException(
            status_code=500,
            detail="M1 model file could not be found",
        )

    except Exception as exc:
        print(f"M1 prediction error: {exc}")

        raise HTTPException(
            status_code=500,
            detail="Could not generate talent prediction",
        )


# ==========================================================
# FINALIZE ASSESSMENT
# ==========================================================

@router.post("/{assessment_id}/finalize")
def finalize_assessment(
    assessment_id: int,
    profile: AthleteProfileInput,
    current_user: dict = Depends(get_current_user),
):
    if current_user["role"].upper() != "ATHLETE":
        raise HTTPException(
            status_code=403,
            detail="Only athletes can finalize assessments",
        )

    try:
        features = get_m1_features_for_assessment(
            assessment_id=assessment_id,
            user_id=current_user["user_id"],
            profile=profile.model_dump(),
        )

        prediction = predict_talent(features)

        result = save_final_prediction(
            assessment_id=assessment_id,
            user_id=current_user["user_id"],
            features=features,
            prediction=prediction,
        )

        return result

    except PermissionError as exc:
        raise HTTPException(
            status_code=403,
            detail=str(exc),
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        )

    except Exception as exc:
        print(f"Assessment finalization error: {exc}")

        raise HTTPException(
            status_code=500,
            detail="Could not finalize assessment",
        )


# ==========================================================
# UPLOAD + PROCESS EXERCISE VIDEO
# ==========================================================

@router.post(
    "/{assessment_id}/exercises/{exercise}",
    response_model=ExerciseResultResponse,
)
async def upload_exercise_video(
    assessment_id: int,
    exercise: str,
    video: UploadFile = File(...),
    height_cm: float | None = Form(default=None),
    current_user: dict = Depends(get_current_user),
):
    # ------------------------------------------------------
    # Athlete authorization
    # ------------------------------------------------------

    if current_user["role"].upper() != "ATHLETE":
        raise HTTPException(
            status_code=403,
            detail="Only athletes can perform assessments",
        )

    # ------------------------------------------------------
    # Normalize exercise name
    # ------------------------------------------------------

    exercise = exercise.lower().strip()

    if exercise not in SUPPORTED_EXERCISES:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported exercise: {exercise}",
        )

    # ------------------------------------------------------
    # Validate video extension
    # ------------------------------------------------------

    filename = video.filename or ""
    extension = os.path.splitext(filename)[1].lower()

    if extension not in ALLOWED_VIDEO_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail="Unsupported video format",
        )

    temp_path = None

    try:
        # --------------------------------------------------
        # Save uploaded video temporarily
        # --------------------------------------------------

        with tempfile.NamedTemporaryFile(
            delete=False,
            suffix=extension,
        ) as temp_file:

            temp_path = temp_file.name

            while True:
                chunk = await video.read(1024 * 1024)

                if not chunk:
                    break

                temp_file.write(chunk)

        # --------------------------------------------------
        # Vertical jump requires athlete height
        # --------------------------------------------------

        athlete_height_cm = None

        if exercise == "vertical_jump":

            # Prefer height supplied by Flutter for this assessment.
            athlete_height_cm = height_cm

            # Fall back to the athlete's saved registration height.
            if athlete_height_cm is None:
                athlete_height_cm = get_athlete_height_cm(
                    current_user["user_id"]
                )

            if athlete_height_cm is None:
                raise HTTPException(
                    status_code=400,
                    detail=(
                        "Athlete height is required "
                        "for vertical jump"
                    ),
                )

            # Reject invalid or non-finite height values.
            if (
                not math.isfinite(athlete_height_cm)
                or not 80 <= athlete_height_cm <= 250
            ):
                raise HTTPException(
                    status_code=400,
                    detail="Height must be between 80 cm and 250 cm.",
                )

        # --------------------------------------------------
        # Run CV analysis
        # --------------------------------------------------

        result = process_exercise_video(
            video_path=temp_path,
            exercise=exercise,
            athlete_height_cm=athlete_height_cm,
        )

        # --------------------------------------------------
        # Save CV result into Oracle
        # --------------------------------------------------

        session_id = save_cv_result(
            assessment_id=assessment_id,
            user_id=current_user["user_id"],
            result=result,
        )

        # --------------------------------------------------
        # Return result
        # --------------------------------------------------

        return {
            "assessment_id": assessment_id,
            "session_id": session_id,
            "exercise": exercise,
            "status": result["status"],
            "valid_reps": result["valid_reps"],
            "measurement": result["measurement"],
            "features": result["features"],
            "quality": result["quality"],
        }

    except HTTPException:
        raise

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        )

    except Exception as exc:
        print(f"Exercise processing error: {exc}")

        raise HTTPException(
            status_code=500,
            detail="Exercise processing failed",
        )

    finally:
        # --------------------------------------------------
        # Close uploaded file
        # --------------------------------------------------

        await video.close()

        # --------------------------------------------------
        # Delete temporary video
        # --------------------------------------------------

        if temp_path and os.path.exists(temp_path):
            try:
                os.remove(temp_path)
            except OSError:
                pass





@router.get("/{assessment_id}/result")
def get_assessment_result(
    assessment_id: int,
    current_user: dict = Depends(get_current_user),
):
    import json

    connection = None
    cursor = None

    try:
        connection = get_connection()
        cursor = connection.cursor()

        # 1. Verify assessment ownership and status.
        cursor.execute(
            """
            SELECT USER_ID, STATUS
            FROM ASSESSMENTS
            WHERE ASSESSMENT_ID = :assessment_id
            """,
            {"assessment_id": assessment_id},
        )

        assessment_row = cursor.fetchone()

        if assessment_row is None:
            raise HTTPException(
                status_code=404,
                detail="Assessment not found.",
            )

        assessment_user_id, assessment_status = assessment_row

        if assessment_user_id != current_user["user_id"]:
            raise HTTPException(
                status_code=403,
                detail="You are not allowed to view this assessment.",
            )

        if assessment_status != "COMPLETED":
            raise HTTPException(
                status_code=400,
                detail="Assessment is not completed yet.",
            )

        # 2. Read the saved feature snapshot.
        # These are the 11 features used by M1.
        cursor.execute(
            """
            SELECT
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
            FROM ASSESSMENT_FEATURE_SNAPSHOT
            WHERE ASSESSMENT_ID = :assessment_id
            """,
            {"assessment_id": assessment_id},
        )

        feature_row = cursor.fetchone()

        if feature_row is None:
            raise HTTPException(
                status_code=404,
                detail="Saved assessment features not found.",
            )

        features = {
            "age": feature_row[0],
            "gender": feature_row[1],
            "height_cm": feature_row[2],
            "weight_kg": feature_row[3],
            "pushup_count": feature_row[4],
            "squat_count": feature_row[5],
            "deadlift_reps": feature_row[6],
            "running_50m_seconds": feature_row[7],
            "situp_count": feature_row[8],
            "plank_duration_seconds": feature_row[9],
            "vertical_jump_cm": feature_row[10],
        }

        # Convert Oracle NUMBER values to JSON-safe Python numbers.
        for key, value in features.items():
            if value is not None and hasattr(value, "as_tuple"):
                features[key] = float(value)

        # 3. Read the saved M1 prediction.
        # Column names match your CREATE TABLE statement.
        cursor.execute(
            """
            SELECT
                TALENT_LEVEL,
                CONFIDENCE,
                RECOMMENDED_SPORT,
                STRENGTHS,
                NEEDS_IMPROVEMENT,
                MODEL_VERSION
            FROM ASSESSMENT_PREDICTIONS
            WHERE ASSESSMENT_ID = :assessment_id
            """,
            {"assessment_id": assessment_id},
        )

        prediction_row = cursor.fetchone()

        if prediction_row is None:
            raise HTTPException(
                status_code=404,
                detail="Saved assessment prediction not found.",
            )

        def parse_json_list(value):
            if value is None:
                return []

            if hasattr(value, "read"):
                value = value.read()

            if isinstance(value, list):
                return value

            try:
                parsed = json.loads(value)
                return parsed if isinstance(parsed, list) else [parsed]
            except (TypeError, ValueError):
                return [str(value)]

        prediction = {
            "talent_level": prediction_row[0],
            "confidence": (
                float(prediction_row[1])
                if prediction_row[1] is not None
                else None
            ),
            "recommended_sport": prediction_row[2],
            "strengths": parse_json_list(prediction_row[3]),
            "needs_improvement": parse_json_list(prediction_row[4]),
            "model_version": prediction_row[5],
            "warning": (
                "AI-assisted demonstration only; this is not an official "
                "selection decision. Use qualified coaches and approved, "
                "age-appropriate protocols. Deadlift assessments must use "
                "a safe standard load under trained supervision."
            ),
        }
        # 4. Get recommended coaches based on predicted talent level.
        recommended_coaches = get_recommended_coaches(
        cursor=cursor,
        talent_level=prediction["talent_level"],
            )

        return {
            "assessment_id": assessment_id,
            "status": assessment_status,
            "features": features,
            "prediction": prediction,
            "recommended_coaches": recommended_coaches,
        }

    except HTTPException:
        raise

    except Exception as e:
        print("GET ASSESSMENT RESULT ERROR:", e)
        raise HTTPException(
            status_code=500,
            detail="Could not load assessment result.",
        )

    finally:
        if cursor is not None:
            cursor.close()

        if connection is not None:
            connection.close()


# ==========================================================
# GET ATHLETE ASSESSMENT HISTORY
# Used by Flutter dashboard
# ==========================================================

@router.get("/history/all")
def get_assessment_history(
    current_user: dict = Depends(get_current_user),
):
    connection = None
    cursor = None

    if current_user["role"].upper() != "ATHLETE":
        raise HTTPException(
            status_code=403,
            detail="Only athletes can view assessment history",
        )

    try:
        connection = get_connection()
        cursor = connection.cursor()

        # --------------------------------------------------
        # Dashboard summary
        # --------------------------------------------------

        cursor.execute(
            """
            SELECT
                COUNT(*) AS TOTAL_ASSESSMENTS,
                SUM(
                    CASE
                        WHEN STATUS = 'COMPLETED' THEN 1
                        ELSE 0
                    END
                ) AS COMPLETED_ASSESSMENTS
            FROM ASSESSMENTS
            WHERE USER_ID = :user_id
            """,
            {
                "user_id": current_user["user_id"]
            },
        )

        summary_row = cursor.fetchone()

        total_assessments = (
            int(summary_row[0])
            if summary_row and summary_row[0] is not None
            else 0
        )

        completed_assessments = (
            int(summary_row[1])
            if summary_row and summary_row[1] is not None
            else 0
        )

        in_progress_assessments = (
            total_assessments - completed_assessments
        )

        # --------------------------------------------------
        # Read all assessments + saved M1 predictions
        # --------------------------------------------------

        cursor.execute(
            """
            SELECT
                A.ASSESSMENT_ID,
                A.STATUS,
                A.CREATED_AT,
                A.COMPLETED_AT,
                P.TALENT_LEVEL,
                P.CONFIDENCE,
                P.RECOMMENDED_SPORT,
                P.MODEL_VERSION
            FROM ASSESSMENTS A
            LEFT JOIN ASSESSMENT_PREDICTIONS P
                ON P.ASSESSMENT_ID = A.ASSESSMENT_ID
            WHERE A.USER_ID = :user_id
            ORDER BY A.ASSESSMENT_ID DESC
            """,
            {
                "user_id": current_user["user_id"]
            },
        )

        rows = cursor.fetchall()

        assessments = []

        for row in rows:
            confidence = (
                float(row[5])
                if row[5] is not None
                else None
            )

            assessments.append(
                {
                    "assessment_id": int(row[0]),
                    "status": row[1],
                    "created_at": (
                        row[2].isoformat()
                        if row[2] is not None
                        else None
                    ),
                    "completed_at": (
                        row[3].isoformat()
                        if row[3] is not None
                        else None
                    ),
                    "talent_level": row[4],
                    "confidence": confidence,
                    "recommended_sport": row[6],
                    "model_version": row[7],
                }
            )

        return {
            "summary": {
                "total_assessments": total_assessments,
                "completed_assessments": completed_assessments,
                "in_progress_assessments": in_progress_assessments,
            },
            "assessments": assessments,
        }

    except HTTPException:
        raise

    except Exception as exc:
        print(
            "GET ASSESSMENT HISTORY ERROR:",
            exc,
        )

        raise HTTPException(
            status_code=500,
            detail="Could not load assessment history.",
        )

    finally:
        if cursor is not None:
            cursor.close()

        if connection is not None:
            connection.close()            