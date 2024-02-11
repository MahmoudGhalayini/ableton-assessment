# Copyright 2024 Ableton
# All rights reserved


import uuid
from datetime import datetime, timedelta

import pytest

from core.configuration import (AUTH_TOKEN_EXPIRY_PERIOD,
                                SECRET_KEY,
                                VERIFICATION_TOKEN_EXPIRY_PERIOD)
from core.schemas import UserIn


@pytest.fixture
def new_user() -> UserIn:
    return UserIn(email='example@example.com',
                  first_name='John',
                  last_name='Doe',
                  password='SecurePassword123')


@pytest.fixture
def user_data() -> dict:
    return dict(email='example1@example1.com',
                first_name='John',
                last_name='Doe',
                password='SecurePassword123')


@pytest.fixture
def new_verification_token():
    verification_token = str(uuid.uuid4())
    expiry = datetime.utcnow() + timedelta(minutes=float(VERIFICATION_TOKEN_EXPIRY_PERIOD))

    return {'token': verification_token, 'expiry': expiry}


@pytest.fixture
def new_auth_token():
    expiry = datetime.utcnow() + timedelta(minutes=float(AUTH_TOKEN_EXPIRY_PERIOD))

    return {'expiry': expiry, 'secret_key': SECRET_KEY, 'algorithm': 'HS256'}
