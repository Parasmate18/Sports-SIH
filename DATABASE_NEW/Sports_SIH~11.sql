CREATE TABLE CV_MEASUREMENTS (
    MEASUREMENT_ID NUMBER
        GENERATED ALWAYS AS IDENTITY
        PRIMARY KEY,

    SESSION_ID NUMBER NOT NULL,

    FEATURE_NAME VARCHAR2(50) NOT NULL,

    FEATURE_VALUE NUMBER(10,2) NOT NULL,

    CREATED_AT TIMESTAMP
        DEFAULT CURRENT_TIMESTAMP
        NOT NULL,

    CONSTRAINT FK_CV_MEASUREMENT_SESSION
        FOREIGN KEY (SESSION_ID)
        REFERENCES CV_SESSION_RESULTS(SESSION_ID)
        ON DELETE CASCADE,

    CONSTRAINT UQ_CV_MEASUREMENT_FEATURE
        UNIQUE (SESSION_ID, FEATURE_NAME),

    CONSTRAINT CHK_CV_MEASUREMENT_FEATURE
        CHECK (
            FEATURE_NAME IN (
                'pushup_count',
                'squat_count',
                'deadlift_reps',
                'running_50m_seconds',
                'situp_count',
                'plank_duration_seconds',
                'vertical_jump_cm'
            )
        )
);