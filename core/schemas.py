# Copyright 2024 Ableton
# All rights reserved


from dataclasses import dataclass

from core.helpers import ValidationMixin


@dataclass
class InternalUser:
    id: int
    email: str
    first_name: str
    last_name: str
    password: str
    email_verified: bool


@dataclass
class User:
    id: int
    email: str
    first_name: str
    last_name: str
    email_verified: bool


@dataclass
class UserIn(ValidationMixin):
    email: str
    first_name: str
    last_name: str
    password: str

    def __post_init__(self):
        if not self.is_non_empty_string(self.email):
            raise ValueError('Email is required.')
        if not self.is_valid_email(self.email):
            raise ValueError(f'Invalid email format: {self.email}')
        if not self.is_non_empty_string(self.first_name):
            raise ValueError('First name is required.')
        if not self.is_non_empty_string(self.last_name):
            raise ValueError('Last name is required.')
        if not self.is_non_empty_string(self.password):
            raise ValueError('Password is required.')
        if not self.password_strength(self.password):
            message = 'Password must be at least 8 characters long and include both letters and numbers only.'
            raise ValueError(message)


@dataclass
class UserVerificationToken:
    id: int
    user_id: int
    token: str
    expiry: str


@dataclass
class Credentials(ValidationMixin):
    email: str
    password: str

    def __post_init__(self):
        if not self.is_valid_email(self.email):
            raise ValueError(f'Invalid email format: {self.email}')
        if not self.is_non_empty_string(self.password):
            raise ValueError('Password is required.')
