import logging

from asyncpg import UniqueViolationError
from databases.core import Connection
from fastapi import Depends

from app.model.user import User
from app.repository import UserAlreadyExistsError, UserNotFoundError
from app.repository.postgres import user_query, get_db_connection


class UserRepository:
    def __init__(self, db_conn: Connection):
        self.db_conn = db_conn

    async def insert_user(
        self, email: str, password: str, first_name: str, last_name: str, two_factor_enabled: bool
    ) -> str:
        query = user_query.insert_user
        values = {
            "email": email,
            "password": password,
            "first_name": first_name,
            "last_name": last_name,
            "two_factor_enabled": two_factor_enabled,
        }
        try:
            user_uuid = await self.db_conn.execute(query=query, values=values)
            return str(user_uuid)
        except UniqueViolationError as e:
            logging.exception(e)
            raise UserAlreadyExistsError("User already exists")

    async def get_user_by_email(self, email: str) -> User:
        query = user_query.get_user_by_email
        values = {"email": email}
        user = await self.db_conn.fetch_one(query=query, values=values)
        if user is None:
            raise UserNotFoundError("User not found")
        return User.from_db(user)


def get_user_repository(db_conn: Connection = Depends(get_db_connection)) -> UserRepository:
    return UserRepository(db_conn=db_conn)
