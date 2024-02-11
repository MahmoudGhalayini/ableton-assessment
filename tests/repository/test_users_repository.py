# Copyright 2024 Ableton
# All rights reserved


from core.database_manager import DatabaseManager
from core.schemas import UserIn
from tests.fixtures import new_user


def test_new_user_insertion(new_user: UserIn, db: DatabaseManager) -> None:
    user_id = db.user_repository.insert_user(new_user)

    assert user_id


def test_get_user_by_id(new_user: UserIn, db: DatabaseManager) -> None:
    user_id = db.user_repository.insert_user(new_user)

    user = db.user_repository.get_user_by_id(id_=user_id)
    assert user.email == new_user.email
    assert user.first_name == new_user.first_name
    assert user.last_name == new_user.last_name


def test_get_user_get_by_email(new_user: UserIn, db: DatabaseManager) -> None:
    db.user_repository.insert_user(new_user)

    user = db.user_repository.get_internal_user_by_email(email=new_user.email)
    assert user.email == new_user.email
    assert user.first_name == new_user.first_name
    assert user.last_name == new_user.last_name
    assert user.email_verified is False


def test_user_email_verification(new_user: UserIn, db: DatabaseManager) -> None:
    db.user_repository.insert_user(new_user)

    user = db.user_repository.get_internal_user_by_email(email=new_user.email)
    assert user.email_verified is False

    db.user_repository.verify_user(id_=user.id)
    verified_user = db.user_repository.get_internal_user_by_email(
        email=user.email)
    assert verified_user.email_verified is True


def test_get_user_by_invalid_id(new_user: UserIn, db: DatabaseManager) -> None:
    invalid_id = 2
    user_id = db.user_repository.insert_user(new_user)

    assert user_id != invalid_id
    user = db.user_repository.get_user_by_id(id_=invalid_id)

    assert user is None


def test_get_user_by_invalid_email(new_user: UserIn, db: DatabaseManager) -> None:
    user_id = db.user_repository.insert_user(new_user)
    user = db.user_repository.get_user_by_id(id_=user_id)

    invalid_email = 'invalid@email.com'
    assert user.email != invalid_email

    user = db.user_repository.get_internal_user_by_email(email=invalid_email)
    assert user is None
