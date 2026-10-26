import importlib

import jwt
import pytest
from fastapi import HTTPException


@pytest.fixture
def oauth2(monkeypatch):
    monkeypatch.setenv("PROD_DB_URL", "sqlite://")
    monkeypatch.setenv("SECRET_KEY", "x" * 64)
    monkeypatch.setenv("ACCESS_TOKEN_EXPIRE_MINUTES", "15")
    return importlib.import_module("services.authentication.oauth2")


def test_access_tokens_use_hs256(oauth2):
    token = oauth2.create_access_token({"username": "test-user"})

    assert jwt.get_unverified_header(token)["alg"] == "HS256"
    assert oauth2.verify_token_access(
        token, HTTPException(status_code=401)
    ).username == "test-user"


def test_access_token_verification_rejects_other_algorithms(oauth2):
    token = jwt.encode(
        {"username": "test-user"},
        "x" * 64,
        algorithm="HS512",
    )

    with pytest.raises(HTTPException) as error:
        oauth2.verify_token_access(token, HTTPException(status_code=401))

    assert error.value.status_code == 401
