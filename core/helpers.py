# Copyright 2024 Ableton
# All rights reserved


import inspect
import re
from dataclasses import fields
from datetime import datetime
from functools import wraps
from typing import Any, Dict, Tuple, Type, TypeVar
from urllib.parse import parse_qs

import jwt

from core.configuration import SECRET_KEY

T = TypeVar('T', bound='ValidationMixin')


class ValidationMixin:
    @staticmethod
    def is_valid_email(email: str) -> bool:
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None

    @staticmethod
    def is_non_empty_string(string: str) -> bool:
        return isinstance(string, str) and bool(string.strip())

    @staticmethod
    def password_strength(password: str) -> bool:
        pattern = r'^(?=.*[A-Za-z])(?=.*\d)[A-Za-z\d]{8,}$'
        return re.match(pattern, password) is not None

    @classmethod
    def from_dict(cls: Type[T], request: Dict[str, Any]) -> T:
        required_keys = {field.name for field in fields(cls)}
        request_keys = set(request.keys())

        missing_keys = sorted(required_keys - request_keys)
        extra_keys = sorted(request_keys - required_keys)

        if missing_keys:
            raise ValueError(
                f"Request is missing required key(s): {', '.join(missing_keys)}.")

        if extra_keys:
            raise ValueError(
                f"Request contains unrecognized key(s): {', '.join(extra_keys)}.")

        return cls(**request)  # type: ignore


def parse_query_params(query_string: str) -> dict:
    query_params = parse_qs(query_string)

    return {key: value[0] if len(value) == 1 else value for key, value in query_params.items()}


def argument_injector(func):
    @wraps(func)
    def wrapper(**kwargs):
        sig = inspect.signature(func)
        func_kwargs = {k: v for k, v in kwargs.items() if k in sig.parameters}

        return func(**func_kwargs)
    return wrapper


def decode_jwt(token: str) -> Tuple[str, datetime]:
    if token.startswith('Bearer '):
        token = token[7:]

    decoded_token = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])

    return decoded_token['user_id'], decoded_token['expiry']
