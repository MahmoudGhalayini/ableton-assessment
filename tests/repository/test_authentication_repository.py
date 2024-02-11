# Copyright 2024 Ableton
# All rights reserved


from datetime import datetime

import jwt

from core.database_manager import DatabaseManager
from core.schemas import InternalUser, UserIn, UserVerificationToken
from tests.fixtures import new_auth_token, new_user, new_verification_token


def insert_user(new_user: UserIn, db: DatabaseManager) -> InternalUser:
    db.user_repository.insert_user(new_user)

    return db.user_repository.get_internal_user_by_email(email=new_user.email)


def insert_verification_token(new_verification_token: dict, user_id: int, db: DatabaseManager) -> UserVerificationToken:
    return db.verification_repository.insert_verification_token(user_id=user_id,
                                                                token=new_verification_token['token'],
                                                                expiry=new_verification_token['expiry'])


def insert_auth_token(new_auth_token: dict, user_id: int, db: DatabaseManager) -> int:
    token = jwt.encode({'user_id': user_id, 'expiry': new_auth_token['expiry'].isoformat()},
                       new_auth_token['secret_key'],
                       algorithm=new_auth_token['algorithm'])
    token_id = db.auth_repository.insert_auth_token(user_id=user_id,
                                                    token=token,
                                                    expiry=new_auth_token['expiry'])

    return token, token_id


def test_insert_verification_token(new_user: UserIn, new_verification_token: dict, db: DatabaseManager) -> None:
    user = insert_user(new_user, db)

    token_id = insert_verification_token(new_verification_token,
                                         user.id,
                                         db)
    assert token_id


def test_get_verification_token_by_token(new_user: UserIn, new_verification_token: dict, db: DatabaseManager) -> None:
    user = insert_user(new_user, db)

    insert_verification_token(new_verification_token,
                              user.id,
                              db)

    token = db.verification_repository.get_verification_token(
        token=new_verification_token['token'])
    assert token.token == new_verification_token['token']

    expiry = datetime.strptime(token.expiry, '%Y-%m-%d %H:%M:%S.%f')
    assert expiry == new_verification_token['expiry']


def test_get_verification_token_by_id(new_user: UserIn, new_verification_token: dict, db: DatabaseManager) -> None:
    user = insert_user(new_user, db)

    token_id = insert_verification_token(new_verification_token,
                                         user.id,
                                         db)

    verification_token = db.verification_repository.get_verification_token_by_id(
        id_=token_id)
    assert verification_token.token == new_verification_token['token']

    expiry = datetime.strptime(verification_token.expiry,
                               '%Y-%m-%d %H:%M:%S.%f')
    assert expiry == new_verification_token['expiry']


def test_delete_verification_token(new_user: UserIn, new_verification_token: dict, db: DatabaseManager) -> None:
    user = insert_user(new_user, db)

    token_id = insert_verification_token(new_verification_token,
                                         user.id,
                                         db)
    assert token_id

    db.verification_repository.delete_verification_token(
        token=new_verification_token['token'])
    token = db.verification_repository.get_verification_token(
        token=new_verification_token['token'])
    assert token is None


def test_insert_auth_token(new_user: UserIn, new_auth_token: dict, db: DatabaseManager) -> None:
    user = insert_user(new_user, db)

    _, token_id = insert_auth_token(new_auth_token, user.id, db)

    assert token_id


def test_get_auth_token_by_user_id(new_user: UserIn, new_auth_token: dict, db: DatabaseManager) -> None:
    user = insert_user(new_user, db)

    token, _ = insert_auth_token(new_auth_token, user.id, db)

    new_token = db.auth_repository.get_auth_token_user_by_id(
        user.id)

    assert token == new_token
