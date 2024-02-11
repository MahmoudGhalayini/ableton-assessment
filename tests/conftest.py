# Copyright 2024 Ableton
# All rights reserved


import os
import threading

import httpx
import pytest

from core.database_manager import DatabaseManager
from main import run, ServerThread


@pytest.fixture
def db():
    db_path = 'ableton_user_management.db'

    yield DatabaseManager(db_path)

    os.remove(db_path)


@pytest.fixture(scope='module')
def client():
    httpd = run(port=8001)
    server_thread = ServerThread(httpd)
    server_thread.start()

    client = httpx.Client(base_url='http://localhost:8001')

    yield client

    client.close()
    server_thread.stop_server()
    server_thread.join()
