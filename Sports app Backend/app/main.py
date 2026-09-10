from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.auth import router as auth_router
from app.db.connection import get_connection
from app.api.users import router as users_router
from app.api.assessments import router as assessments_router

app = FastAPI(
    title="Sports Talent Assessment API",
    version="1.0.0",
)
app.add_middleware(
    CORSMiddleware,
    allow_origin_regex=r"http://(localhost|127\.0\.0\.1):\d+",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(auth_router)
app.include_router(users_router)
app.include_router(assessments_router)


@app.get("/")
def root():
    return {"message": "Sports Talent Assessment Backend"}


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/health/database")
def database_health():
    connection = None
    cursor = None

    try:
        connection = get_connection()
        cursor = connection.cursor()
        cursor.execute("SELECT 1 FROM DUAL")
        result = cursor.fetchone()

        return {
            "status": "ok",
            "database": "Oracle",
            "test_query": result[0],
        }

    except Exception:
        return {
            "status": "error",
            "detail": "Database connection failed",
        }

    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()