create or replace NONEDITIONABLE PACKAGE BODY USER_MANAGEMENT AS

    PROCEDURE INSERT_USER_DETAILS
                            (
                                P_ROLE         IN  USER_DETAILS.ROLE%TYPE,
                                P_FNM          IN  USER_DETAILS.FNM%TYPE,
                                P_LNM          IN  USER_DETAILS.LNM%TYPE,
                                P_MOB_NO       IN  USER_DETAILS.MOB_NO%TYPE,
                                P_AGE          IN  USER_DETAILS.AGE%TYPE,
                                P_GENDER       IN  USER_DETAILS.GENDER%TYPE,
                                P_USERNAME     IN  USER_DETAILS.USERNAME%TYPE,
                                P_PASSWORD     IN  USER_DETAILS.PASSWORD%TYPE,
                                P_ADDR_LINE_1  IN  USER_DETAILS.ADDR_LINE_1%TYPE DEFAULT NULL,
                                P_DIST         IN  USER_DETAILS.DIST%TYPE        DEFAULT NULL,
                                P_PSTL_CD      IN  USER_DETAILS.PSTL_CD%TYPE     DEFAULT NULL,
                                P_STATE        IN  USER_DETAILS.STATE%TYPE       DEFAULT NULL,
                                P_COUNTRY      IN  USER_DETAILS.COUNTRY%TYPE     DEFAULT 'INDIA',
                                P_WGT          IN  USER_DETAILS.WGT%TYPE         DEFAULT NULL,
                                P_HGT          IN  USER_DETAILS.HGT%TYPE         DEFAULT NULL,
                                O_STATUS       OUT VARCHAR2,
                                O_MESSAGE      OUT VARCHAR2
                            ) IS
        V_COUNT         NUMBER := 0;
        V_ROLE          USER_DETAILS.ROLE%TYPE := UPPER(TRIM(P_ROLE));
        V_FNM           USER_DETAILS.FNM%TYPE := UPPER(TRIM(P_FNM));
        V_LNM           USER_DETAILS.LNM%TYPE := UPPER(TRIM(P_LNM));
        V_MOB_NO        USER_DETAILS.MOB_NO%TYPE := TRIM(P_MOB_NO);
        V_AGE           USER_DETAILS.AGE%TYPE := TRIM(P_AGE);
        V_GENDER        USER_DETAILS.GENDER%TYPE := UPPER(TRIM(P_GENDER));
        V_USERNAME      USER_DETAILS.USERNAME%TYPE := TRIM(P_USERNAME);
        V_PASSWORD      USER_DETAILS.PASSWORD%TYPE := TRIM(P_PASSWORD);
        V_ADDR_LINE_1   USER_DETAILS.ADDR_LINE_1%TYPE := UPPER(TRIM(P_ADDR_LINE_1));
        V_DIST          USER_DETAILS.DIST%TYPE := UPPER(TRIM(P_DIST));
        V_PSTL_CD       USER_DETAILS.PSTL_CD%TYPE := TRIM(P_PSTL_CD);
        V_STATE         USER_DETAILS.STATE%TYPE := UPPER(TRIM(P_STATE));
        V_COUNTRY       USER_DETAILS.COUNTRY%TYPE := UPPER(NVL(TRIM(P_COUNTRY), 'INDIA'));
        V_WGT           USER_DETAILS.WGT%TYPE := TRIM(P_WGT);
        V_HGT           USER_DETAILS.HGT%TYPE := TRIM(P_HGT);
    BEGIN
        BEGIN
            SELECT 
                COUNT(1)
            INTO
                V_COUNT
            FROM
                USER_DETAILS
            WHERE
                USERNAME = V_USERNAME;

            IF V_COUNT > 0 THEN
                O_STATUS  := 'FAILED';
                O_MESSAGE := 'Username exists.  Try with different username.';
                RETURN;
            END IF;
        END;
        
        BEGIN
            SELECT
                COUNT(1)
            INTO
                V_COUNT
            FROM
                USER_DETAILS UD
            WHERE
                UD.FNM = V_FNM
                AND UD.LNM = V_LNM
                AND UD.ADDR_LINE_1 = V_ADDR_LINE_1
                AND UD.DIST = V_DIST
                AND UD.PSTL_CD = V_PSTL_CD
                AND UD.STATE = V_STATE;
                
            IF V_COUNT > 0 THEN
                O_STATUS  := 'FAILED';
                O_MESSAGE := 'User details already existed.  Try to login with your login credentials.';
                RETURN;
            END IF;
        END;
        
        IF V_COUNT = 0 THEN
            INSERT INTO USER_DETAILS (
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
                PASSWORD,
                WGT,
                HGT
            ) VALUES (
                V_ROLE,
                V_FNM,
                V_LNM,
                V_MOB_NO,
                V_AGE,
                V_GENDER,
                V_ADDR_LINE_1,
                V_DIST,
                V_PSTL_CD,
                V_STATE,
                V_COUNTRY,
                V_USERNAME,
                V_PASSWORD,
                V_WGT,
                V_HGT
            );

            O_STATUS  := 'SUCCESS';
            O_MESSAGE := 'Registration successful.';
        END IF;
    
        EXCEPTION
            WHEN OTHERS THEN
                O_STATUS  := 'FAILED';
                O_MESSAGE := 'Registration failed: ' || SQLERRM;
    END INSERT_USER_DETAILS;

END USER_MANAGEMENT;