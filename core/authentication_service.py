# Copyright 2024 Ableton
# All rights reserved


import uuid
from dataclasses import asdict
from datetime import datetime, timedelta
from sqlite3 import Error

import bcrypt  # type: ignore
import jwt

from core.configuration import (AUTH_TOKEN_EXPIRY_PERIOD,
                                SECRET_KEY,
                                VERIFICATION_TOKEN_EXPIRY_PERIOD)
from core.database_manager import DatabaseManager
from core.helpers import decode_jwt
from core.schemas import Credentials, User, UserIn


def register(data: dict, db: DatabaseManager) -> dict:
    try:
        user_in = UserIn.from_dict(data)
        user_in.password = bcrypt.hashpw(user_in.password.encode('utf-8'),
                                         bcrypt.gensalt())
        user_in.email = user_in.email.lower()
        user_id = db.user_repository.insert_user(user_in)

        user = User(id=user_id,
                    email=user_in.email,
                    first_name=user_in.first_name,
                    last_name=user_in.last_name,
                    email_verified=False)

        verification_token = str(uuid.uuid4())
        expiry = datetime.utcnow() + timedelta(minutes=float(VERIFICATION_TOKEN_EXPIRY_PERIOD))
        db.verification_repository.insert_verification_token(user_id=user_id,
                                                                 token=verification_token,
                                                                 expiry=expiry)

        message = f'''For demo purposes, please use the following link for email verification: http://localhost:5000/verify-email?token={verification_token}'''  # pylint: disable=line-too-long

        return {'data': asdict(user),
                'message': message,
                'status_code': 201}

    except ValueError as exc:
        return {'message': str(exc), 'status_code': 400}
    except Error as exc:
        return {'message': str(exc), 'status_code': 400}


def verify_email(query_params: dict, db: DatabaseManager) -> dict:
    if not query_params and not query_params.get('token', None):
        return {'message': 'Bad Request', 'status_code': 400}
    try:
        token = query_params.get('token', None)
        verification_token = db.verification_repository.get_verification_token(
            token=token)
        if not verification_token:
            return {'message': 'Bad Request', 'status_code': 400}

        expiry = datetime.strptime(verification_token.expiry,
                                   '%Y-%m-%d %H:%M:%S.%f')
        if expiry < datetime.utcnow():
            return {'message': 'Token Expired', 'status_code': 400}

        user = db.user_repository.get_user_by_id(id_=verification_token.user_id)
        if not user:
            return {'message': 'Bad Request', 'status_code': 400}

        db.user_repository.verify_user(id_=verification_token.user_id)
        db.verification_repository.delete_verification_token(token=token)

        return {'message': f'Email verified for user: {user.email}', 'status_code': 200}

    except Error as exc:
        return {'message': str(exc), 'status_code': 400}


def authenticate(data: dict, db: DatabaseManager) -> dict:
    try:
        credentials = Credentials.from_dict(data)

        user = db.user_repository.get_internal_user_by_email(
            email=credentials.email.lower())
        if not user:
            return {'message': 'Invalid credentials', 'status_code': 401}
        if user.email_verified is False:
            return {'message': 'Email not verified, please verify your email.', 'status_code': 403}

        if bcrypt.checkpw(credentials.password.encode('utf-8'), user.password):
            expiry = datetime.utcnow() + timedelta(minutes=float(AUTH_TOKEN_EXPIRY_PERIOD))
            token = jwt.encode({'user_id': user.id, 'expiry': expiry.isoformat()},
                               SECRET_KEY,
                               algorithm='HS256')
            db.auth_repository.insert_auth_token(user_id=user.id,
                                                               token=token,
                                                               expiry=expiry)

            return {'data': {'access_token': token}, 'status_code': 200}

        return {'message': 'Invalid credentials', 'status_code': 401}

    except ValueError as exc:
        return {'message': str(exc), 'status_code': 400}
    except Error as exc:
        return {'message': str(exc), 'status_code': 400}


def get_current_logged_user(headers: dict, db: DatabaseManager) -> dict:
    user_id, _ = decode_jwt(token=headers.get('Authorization', ''))
    user = db.user_repository.get_user_by_id(id_=int(user_id))

    return {'data': asdict(user), 'status_code': 200}
