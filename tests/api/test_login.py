# Copyright 2024 Ableton
# All rights reserved


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


def verify_email(token: str, client: Client) -> None:
    verify_email_response = client.get('/verify-email',
                                       params={'token': token})

    assert verify_email_response.status_code == 200


def test_login(user_data: dict, client: Client, db: DatabaseManager) -> None:
    data, token = register_user(data=user_data, client=client)

    assert data['email_verified'] is False

    verify_email(token=token, client=client)

    credentials = {'email': user_data['email'],
                   'password': user_data['password']}
    login_response = client.post('/login', json=credentials)
    json_response = login_response.json()

    assert json_response['data']['access_token']
    assert login_response.status_code == 200


def test_login_without_email_verification(user_data: dict, client: Client, db: DatabaseManager) -> None:
    data, _ = register_user(data=user_data, client=client)

    assert data['email_verified'] is False

    credentials = {'email': user_data['email'],
                   'password': user_data['password']}
    login_response = client.post('/login', json=credentials)
    json_response = login_response.json()

    assert login_response.status_code == 403
    assert json_response['message'] == 'Email not verified, please verify your email.'


def test_login_with_invalid_email(user_data: dict, client: Client, db: DatabaseManager) -> None:
    data, token = register_user(data=user_data, client=client)

    assert data['email_verified'] is False

    verify_email(token=token, client=client)

    credentials = {'email': 'email@email.com',
                   'password': user_data['password']}
    login_response = client.post('/login', json=credentials)
    json_response = login_response.json()

    assert login_response.status_code == 401
    assert json_response['message'] == 'Invalid credentials'


def test_login_with_invalid_password(user_data: dict, client: Client, db: DatabaseManager) -> None:
    data, token = register_user(data=user_data, client=client)

    assert data['email_verified'] is False

    verify_email(token=token, client=client)

    credentials = {'email': user_data['email'],
                   'password': 'password'}
    login_response = client.post('/login', json=credentials)
    json_response = login_response.json()

    assert login_response.status_code == 401
    assert json_response['message'] == 'Invalid credentials'
