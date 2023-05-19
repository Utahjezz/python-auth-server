import pytest
from asyncpg import UniqueViolationError
from databases.core import Connection
from pydantic import SecretStr

from app.repository import UserAlreadyExistsError, UserNotFoundError
from app.repository.postgres.user import UserRepository


@pytest.mark.asyncio
async def test_insert_user_success(mocker, create_user_request):
    db_conn = mocker.Mock(spec=Connection)
    db_conn.execute.return_value = "1"
    _input = create_user_request

    user_repository = UserRepository(db_conn=db_conn)
    user_id = await user_repository.insert_user(**_input)

    assert user_id == "1"
    db_conn.execute.assert_called_once_with(
        query="""
insert into users (email, password, first_name, last_name, two_factor_enabled)
    values (:email, :password, :first_name, :last_name, :two_factor_enabled)
returning id
""",
        values=_input,
    )


@pytest.mark.asyncio
async def test_insert_user_failure(mocker, create_user_request):
    db_conn = mocker.Mock(spec=Connection)
    db_conn.execute.side_effect = UniqueViolationError("error")
    _input = create_user_request

    user_repository = UserRepository(db_conn=db_conn)

    with pytest.raises(UserAlreadyExistsError):
        await user_repository.insert_user(**_input)


@pytest.mark.asyncio
async def test_get_user_by_email_success(mocker, create_user_request):
    db_conn = mocker.Mock(spec=Connection)
    db_conn.fetch_one.return_value = dict(**create_user_request, id="1")
    _input = create_user_request

    user_repository = UserRepository(db_conn=db_conn)
    user = await user_repository.get_user_by_email(_input["email"])

    assert user.id == "1"
    assert user.email == _input["email"]
    assert user.password == SecretStr(_input["password"])
    assert user.first_name == _input["first_name"]
    assert user.last_name == _input["last_name"]
    assert user.two_factor_enabled == _input["two_factor_enabled"]
    db_conn.fetch_one.assert_called_once_with(
        query="""
select id, email, password, first_name, last_name, two_factor_enabled
    from users
    where email = :email
""",
        values={"email": _input["email"]},
    )


@pytest.mark.asyncio
async def test_get_user_by_email_not_found(mocker, create_user_request):
    db_conn = mocker.Mock(spec=Connection)
    db_conn.fetch_one.return_value = None
    _input = create_user_request

    user_repository = UserRepository(db_conn=db_conn)

    with pytest.raises(UserNotFoundError):
        await user_repository.get_user_by_email(_input["email"])


@pytest.mark.asyncio
async def test_get_user_by_id_success(mocker, create_user_request):
    db_conn = mocker.Mock(spec=Connection)
    db_conn.fetch_one.return_value = dict(**create_user_request, id="1")
    _input = create_user_request

    user_repository = UserRepository(db_conn=db_conn)
    user = await user_repository.get_user_by_id("1")

    assert user.id == "1"
    assert user.email == _input["email"]
    assert user.password == SecretStr(_input["password"])
    assert user.first_name == _input["first_name"]
    assert user.last_name == _input["last_name"]
    assert user.two_factor_enabled == _input["two_factor_enabled"]
    db_conn.fetch_one.assert_called_once_with(
        query="""
select id, email, password, first_name, last_name, two_factor_enabled
    from users
    where id = :id
""",
        values={"id": "1"},
    )


@pytest.mark.asyncio
async def test_get_user_by_id_not_found(mocker, create_user_request):
    db_conn = mocker.Mock(spec=Connection)
    db_conn.fetch_one.return_value = None

    user_repository = UserRepository(db_conn=db_conn)

    with pytest.raises(UserNotFoundError):
        await user_repository.get_user_by_id("1")
