# Copyright 2024 Ableton
# All rights reserved


from contextlib import contextmanager
from typing import Generator

from core.database_manager import DatabaseManager


@contextmanager
def get_db() -> Generator[DatabaseManager, None, None]:
    db = DatabaseManager()
    try:
        yield db
    finally:
        db.close()
