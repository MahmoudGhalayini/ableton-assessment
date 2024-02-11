# Copyright 2024 Ableton
# All rights reserved


from typing import Dict, Tuple

from httpx import Client

from core.database_manager import DatabaseManager
from tests.fixtures import user_data


def register_user(data: dict, client: Client) -> Tuple[Dict, int]:
    response = client.post('/register', json=data)

    assert response.status_code == 201
    json_response = response.json()

    return json_response['data'], response.status_code


def invalid_registration(data: dict, client: Client) -> Dict:
    response = client.post('/register', json=data)

    assert response.status_code == 400

    return response.json()


def test_user_registration(user_data: dict, client: Client, db: DatabaseManager) -> None:
    data, _ = register_user(data=user_data, client=client)

    assert data['email'] == user_data['email']
    assert data['first_name'] == user_data['first_name']
    assert data['last_name'] == user_data['last_name']
    assert data['email_verified'] is False


def test_email_unique_constraint(user_data: dict, client: Client, db: DatabaseManager) -> None:
    register_user(data=user_data, client=client)

    response = invalid_registration(data=user_data, client=client)
    assert response['message'] == 'Your request could not be processed. Please try again.'


def test_invalid_email(user_data: dict, client: Client, db: DatabaseManager) -> None:
    user_data['email'] = 'example@example'

    response = invalid_registration(data=user_data, client=client)
    assert response['message'] == f"Invalid email format: {user_data['email']}"


def test_invalid_password(user_data: dict, client: Client, db: DatabaseManager) -> None:
    user_data['password'] = '1234'

    response = invalid_registration(data=user_data, client=client)
    assert response['message'] == 'Password must be at least 8 characters long and include both letters and numbers only.'


def test_empty_email(user_data: dict, client: Client, db: DatabaseManager) -> None:
    user_data['email'] = ''

    response = invalid_registration(data=user_data, client=client)
    assert response['message'] == 'Email is required.'


def test_empty_first_name(user_data: dict, client: Client, db: DatabaseManager) -> None:
    user_data['first_name'] = ''

    response = invalid_registration(data=user_data, client=client)
    assert response['message'] == 'First name is required.'


def test_empty_last_name(user_data: dict, client: Client, db: DatabaseManager) -> None:
    user_data['last_name'] = ''

    response = invalid_registration(data=user_data, client=client)
    assert response['message'] == 'Last name is required.'


def test_empty_password(user_data: dict, client: Client, db: DatabaseManager) -> None:
    user_data['password'] = ''

    response = invalid_registration(data=user_data, client=client)
    assert response['message'] == 'Password is required.'


def test_null_email(user_data: dict, client: Client, db: DatabaseManager) -> None:
    user_data['email'] = None

    response = invalid_registration(data=user_data, client=client)
    assert response['message'] == 'Email is required.'


def test_null_first_name(user_data: dict, client: Client, db: DatabaseManager) -> None:
    user_data['first_name'] = None

    response = invalid_registration(data=user_data, client=client)
    assert response['message'] == 'First name is required.'


def test_null_last_name(user_data: dict, client: Client, db: DatabaseManager) -> None:
    user_data['last_name'] = None

    response = invalid_registration(data=user_data, client=client)
    assert response['message'] == 'Last name is required.'


def test_null_password(user_data: dict, client: Client, db: DatabaseManager) -> None:
    user_data['password'] = None

    response = invalid_registration(data=user_data, client=client)
    assert response['message'] == 'Password is required.'


def test_excluding_email(user_data: dict, client: Client, db: DatabaseManager) -> None:
    del user_data['email']

    response = invalid_registration(data=user_data, client=client)
    assert response['message'] == 'Request is missing required key(s): email.'


def test_excluding_first_name(user_data: dict, client: Client, db: DatabaseManager) -> None:
    del user_data['first_name']

    response = invalid_registration(data=user_data, client=client)
    assert response['message'] == 'Request is missing required key(s): first_name.'


def test_excluding_last_name(user_data: dict, client: Client, db: DatabaseManager) -> None:
    del user_data['last_name']

    response = invalid_registration(data=user_data, client=client)
    assert response['message'] == 'Request is missing required key(s): last_name.'


def test_excluding_password(user_data: dict, client: Client, db: DatabaseManager) -> None:
    del user_data['password']

    response = invalid_registration(data=user_data, client=client)
    assert response['message'] == 'Request is missing required key(s): password.'


def test_excluding_multiple_fields(user_data: dict, client: Client, db: DatabaseManager) -> None:
    del user_data['email']
    del user_data['password']

    response = invalid_registration(data=user_data, client=client)
    assert response['message'] == 'Request is missing required key(s): email, password.'


def test_including_extra_fields(user_data: dict, client: Client, db: DatabaseManager) -> None:
    user_data['extra_field1'] = ''
    user_data['extra_field2'] = ''

    response = invalid_registration(data=user_data, client=client)
    assert response['message'] == 'Request contains unrecognized key(s): extra_field1, extra_field2.'
