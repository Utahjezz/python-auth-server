import json

import httpx
import pytest
from jose import jws

from app.service.auth import OTP_TOKEN_TYPE, ACCESS_TOKEN_TYPE


@pytest.mark.asyncio
async def test_simple_flow():
    user_1 = {
        "email": "joe.doe@mail.com",
        "password": "superpass",
        "first_name": "Joe",
        "last_name": "Doe",
        "two_factor_enabled": False,
    }
    async with httpx.AsyncClient() as client:
        response = await client.post("http://localhost:5050/api/v1/register", json=user_1)
        assert response.status_code == 201
        user_id = response.json()["id"]

        response = await client.post(
            "http://localhost:5050/api/v1/login",
            json={
                "email": user_1["email"],
                "password": user_1["password"],
            },
        )

        assert response.status_code == 200
        access_token = response.json()["access_token"]
        payload = json.loads(jws.get_unverified_claims(access_token))
        assert payload["sub"] == user_id
        assert payload["type"] == ACCESS_TOKEN_TYPE

        response = await client.get(
            "http://localhost:5050/api/v1/login/token/validate",
            headers={"Authorization": f"Bearer {access_token}"},
        )
        assert response.status_code == 200


@pytest.mark.asyncio
async def test_otp_flow():
    user_1 = {
        "email": "joe.doe@mail.com",
        "password": "superpass",
        "first_name": "Joe",
        "last_name": "Doe",
        "two_factor_enabled": True,
    }
    async with httpx.AsyncClient() as client:
        response = await client.post("http://localhost:5050/api/v1/register", json=user_1)
        assert response.status_code == 201
        user_id = response.json()["id"]

        response = await client.post(
            "http://localhost:5050/api/v1/login",
            json={
                "email": user_1["email"],
                "password": user_1["password"],
            },
        )

        assert response.status_code == 200
        otp_token = response.json()["access_token"]
        payload = json.loads(jws.get_unverified_claims(otp_token))
        assert payload["sub"] == user_id
        assert payload["type"] == OTP_TOKEN_TYPE

        response = await client.post(
            "http://localhost:5050/api/v1/login/otp",
            json={
                "otp": "123456",
            },
            headers={"Authorization": f"Bearer {otp_token}"},
        )

        assert response.status_code == 200
        access_token = response.json()["access_token"]
        payload = json.loads(jws.get_unverified_claims(access_token))
        assert payload["sub"] == user_id
        assert payload["type"] == ACCESS_TOKEN_TYPE

        response = await client.get(
            "http://localhost:5050/api/v1/login/token/validate",
            headers={"Authorization": f"Bearer {access_token}"},
        )
        assert response.status_code == 200
