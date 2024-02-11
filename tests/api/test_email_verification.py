# Copyright 2024 Ableton
# All rights reserved


import uuid
from typing import Dict, Tuple

from httpx import Client

from core.database_manager import DatabaseManager
from tests.fixtures import user_data
from tests.helpers import extract_token


def register_user(data: dict, client: Client) -> Tuple[Dict, int]:
    response = client.post('/register', json=data)

    assert response.status_code == 201
    json_response = response.json()

    token = extract_token(json_response['message'])
    assert token

    return json_response['data'], token


def test_email_verification(user_data: dict, client: Client, db: DatabaseManager) -> None:
    data, token = register_user(data=user_data, client=client)

    assert data['email_verified'] is False

    response = client.get('/verify-email',
                          params={'token': token})
    json_response = response.json()

    assert response.status_code == 200
    assert json_response['message'] == f"Email verified for user: {data['email']}"


def test_sending_empty_query_param(user_data: dict, client: Client, db: DatabaseManager) -> None:
    data, _ = register_user(data=user_data, client=client)

    assert data['email_verified'] is False

    response = client.get('/verify-email', params={})
    json_response = response.json()

    assert response.status_code == 400
    assert json_response['message'] == 'Bad Request'


def test_sending_null_query_param(user_data: dict, client: Client, db: DatabaseManager) -> None:
    data, _ = register_user(data=user_data, client=client)

    assert data['email_verified'] is False

    response = client.get('/verify-email', params={'token': None})
    json_response = response.json()

    assert response.status_code == 400
    assert json_response['message'] == 'Bad Request'


def test_sending_invalid_token(user_data: dict, client: Client, db: DatabaseManager) -> None:
    data, _ = register_user(data=user_data, client=client)

    assert data['email_verified'] is False

    response = client.get('/verify-email', params={'token': str(uuid.uuid4())})
    json_response = response.json()

    assert response.status_code == 400
    assert json_response['message'] == 'Bad Request'
