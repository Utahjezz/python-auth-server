import logging

import databases
from databases.core import Connection
from pydantic import SecretStr

from app.config.settings import Settings


def create_db_url(user: str, password: str, host: str, database: str) -> str:
    return f"postgresql://{user}:{password}@{host}/{database}"


def create_database(
    host: str,
    database: str,
    user: SecretStr,
    password: SecretStr,
    min_size_pool: int,
    max_size_pool: int,
) -> databases.Database:
    logging.info("Creating database connection")
    db_url = create_db_url(
        user.get_secret_value(),
        password.get_secret_value(),
        host,
        database,
    )
    database = databases.Database(
        url=db_url,
        min_size=min_size_pool,
        max_size=max_size_pool,
    )
    return database


settings = Settings()
database = create_database(
    host=settings.postgres.host,
    database=settings.postgres.database_name,
    user=settings.postgres.user,
    password=settings.postgres.password,
    min_size_pool=settings.postgres.min_size_pool,
    max_size_pool=settings.postgres.max_size_pool,
)


async def get_db_connection() -> Connection:
    async with database.connection() as connection:
        yield connection
