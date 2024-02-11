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


def authenticate_user(user_data: dict, client: Client) -> None:
    data, token = register_user(data=user_data, client=client)

    assert data['email_verified'] is False

    verify_email_response = client.get('/verify-email',
                                       params={'token': token})

    assert verify_email_response.status_code == 200

    credentials = {'email': user_data['email'],
                   'password': user_data['password']}
    login_response = client.post('/login', json=credentials)
    json_response = login_response.json()

    assert json_response['data']['access_token']
    assert login_response.status_code == 200

    return json_response['data']['access_token']


def test_get_current_logged_in_user(user_data: dict, client: Client, db: DatabaseManager) -> None:
    token = authenticate_user(user_data=user_data, client=client)

    response = client.get('/current-user', headers={'Authorization': token})
    json_response = response.json()

    assert response.status_code == 200
    assert json_response['data']['email'] == user_data['email']
    assert json_response['data']['first_name'] == user_data['first_name']
    assert json_response['data']['last_name'] == user_data['last_name']
    assert json_response['data']['email_verified'] is True


def test_get_current_logged_in_user_with_invalid_token(client: Client, db: DatabaseManager) -> None:
    response = client.get('/current-user',
                          headers={'Authorization': 'invalid token'})
    json_response = response.json()

    assert response.status_code == 401
    assert json_response['message'] == 'Invalid token.'
