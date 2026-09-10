import oracledb

from app.core.config import settings


def get_connection():

    dsn = oracledb.makedsn(
        settings.oracle_host,
        settings.oracle_port,
        service_name=settings.oracle_service_name
    )

    connection = oracledb.connect(
        user=settings.oracle_user,
        password=settings.oracle_password,
        dsn=dsn
    )

    return connection