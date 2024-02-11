# Copyright 2024 Ableton
# All rights reserved


import sqlite3
from datetime import datetime
from sqlite3 import Connection, Error, IntegrityError
from typing import Optional

from core.schemas import InternalUser, User, UserIn, UserVerificationToken


class DatabaseManager:
    def __init__(self, db_path: str = 'ableton_user_management.db'):
        self.db_path = db_path
        self.initialize_database()
        self.user_repository = self.UserRepository(self.db)
        self.verification_repository = self.VerificationTokenRepository(
            self.db)
        self.auth_repository = self.AuthenticationTokenRepository(self.db)

    def initialize_database(self) -> None:
        try:
            self.db: Connection = sqlite3.connect(self.db_path)
            self.create_tables()
        except Error as exc:
            print(f'Error connecting to the database: {exc}')

    def create_tables(self) -> None:
        create_users_table_sql = '''CREATE TABLE IF NOT EXISTS users (
                                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                                        email TEXT NOT NULL UNIQUE,
                                        first_name TEXT NOT NULL,
                                        last_name TEXT NOT NULL,
                                        password TEXT NOT NULL,
                                        email_verified BOOLEAN NOT NULL
                                    );'''
        create_verification_tokens_table_sql = '''CREATE TABLE IF NOT EXISTS verification_tokens (
                                                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                                                    user_id INTEGER NOT NULL UNIQUE,
                                                    token TEXT NOT NULL,
                                                    expiry DATETIME NOT NULL,
                                                    FOREIGN KEY (user_id) REFERENCES users(id)
                                                );'''
        create_auth_tokens_table_sql = '''CREATE TABLE IF NOT EXISTS auth_tokens (
                                            token TEXT NOT NULL,
                                            user_id INTEGER NOT NULL,
                                            expiry DATETIME NOT NULL,
                                            FOREIGN KEY (user_id) REFERENCES users(id)
                                        );'''
        try:
            cursor = self.db.cursor()
            cursor.execute(create_users_table_sql)
            cursor.execute(create_verification_tokens_table_sql)
            cursor.execute(create_auth_tokens_table_sql)
            self.db.commit()
        except Error as exc:
            print(f'Error creating the database table(s): {exc}')
            self.db.rollback()
            raise exc

    def close(self):
        if self.db:
            self.db.close()

    class UserRepository:
        def __init__(self, db: Connection):
            self.db = db

        def insert_user(self, user: UserIn) -> int:
            sql = '''INSERT INTO users(email, first_name, last_name, password, email_verified)
                    VALUES(?,?,?,?, False)'''
            try:
                cursor = self.db.cursor()
                cursor.execute(sql, (user.email,
                                     user.first_name,
                                     user.last_name,
                                     user.password))
                self.db.commit()

                return cursor.lastrowid
            except IntegrityError as exc:
                print(exc)
                raise ValueError(
                    'Your request could not be processed. Please try again.') from exc
            except Error as exc:
                raise ValueError(
                    'An error occurred. Please try again later.') from exc

        def get_internal_user_by_email(self, email: str) -> Optional[InternalUser]:
            sql = '''SELECT id, email, first_name, last_name, password, email_verified
                    FROM users
                    WHERE email = ?'''
            try:
                cursor = self.db.cursor()
                cursor.execute(sql, (email,))
                row = cursor.fetchone()
                if row:
                    return InternalUser(id=row[0],
                                        email=row[1],
                                        first_name=row[2],
                                        last_name=row[3],
                                        password=row[4],
                                        email_verified=bool(row[5]))
                return None
            except Error as exc:
                raise exc

        def get_user_by_id(self, id_: int) -> Optional[User]:
            sql = 'SELECT id, email, first_name, last_name, email_verified FROM users WHERE id = ?'
            try:
                cursor = self.db.cursor()
                cursor.execute(sql, (id_,))
                row = cursor.fetchone()
                if row:
                    return User(id=row[0],
                                email=row[1],
                                first_name=row[2],
                                last_name=row[3],
                                email_verified=bool(row[4]))
                return None
            except Error as exc:
                raise exc

        def verify_user(self, id_: int) -> bool:
            sql = 'UPDATE users SET email_verified = true WHERE id = ?'
            try:
                cursor = self.db.cursor()
                cursor.execute(sql, (id_,))
                self.db.commit()

                return cursor.rowcount > 0
            except Error as exc:
                raise exc

    class VerificationTokenRepository:
        def __init__(self, db: Connection):
            self.db = db

        def insert_verification_token(self, user_id: int, token: str, expiry: datetime) -> int:
            sql = 'INSERT INTO verification_tokens(user_id, token, expiry) VALUES(?,?,?)'
            try:
                cursor = self.db.cursor()
                cursor.execute(sql, (user_id, token, expiry))
                self.db.commit()

                return cursor.lastrowid
            except Error as exc:
                raise exc

        def get_verification_token(self, token: str) -> Optional[UserVerificationToken]:
            sql = 'SELECT id, user_id, token, expiry FROM verification_tokens WHERE token = ?'
            try:
                cursor = self.db.cursor()
                cursor.execute(sql, (token,))
                row = cursor.fetchone()
                if row:
                    return UserVerificationToken(id=row[0], user_id=row[1], token=row[2], expiry=row[3])
                return None
            except Error as exc:
                raise exc

        def get_verification_token_by_id(self, id_: int) -> Optional[UserVerificationToken]:
            sql = 'SELECT id, user_id, token, expiry FROM verification_tokens WHERE id = ?'
            try:
                cursor = self.db.cursor()
                cursor.execute(sql, (id_,))
                row = cursor.fetchone()
                if row:
                    return UserVerificationToken(id=row[0], user_id=row[1], token=row[2], expiry=row[3])
                return None
            except Error as exc:
                raise exc

        def delete_verification_token(self, token: str) -> None:
            sql = 'DELETE FROM verification_tokens WHERE token = ?'
            try:
                cursor = self.db.cursor()
                cursor.execute(sql, (token,))
                self.db.commit()
            except Error as exc:
                raise exc

    class AuthenticationTokenRepository:
        def __init__(self, db: Connection):
            self.db = db

        def insert_auth_token(self, user_id: int, token: str, expiry: datetime) -> int:
            sql = 'INSERT INTO auth_tokens(user_id, token, expiry) VALUES(?,?,?)'
            try:
                cursor = self.db.cursor()
                cursor.execute(sql, (user_id, token, expiry))
                self.db.commit()

                return cursor.lastrowid
            except Error as exc:
                raise exc

        def get_auth_token_user_by_id(self, user_id: int) -> str:
            sql = 'SELECT token FROM auth_tokens WHERE user_id = ?'
            try:
                cursor = self.db.cursor()
                cursor.execute(sql, (user_id,))
                row = cursor.fetchone()

                return row[0] if row else None
            except Error as exc:
                raise exc
