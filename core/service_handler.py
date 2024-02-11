# Copyright 2024 Ableton
# All rights reserved


import json
from http.server import BaseHTTPRequestHandler
from typing import Any, Dict
from urllib.parse import urlparse

import jwt

from core.authentication_service import (authenticate,
                                         get_current_logged_user,
                                         register,
                                         verify_email)
from core.dependencies import get_db
from core.helpers import argument_injector, decode_jwt, parse_query_params


def health_check():
    return {'message': 'OK', 'status_code': 200}


class ServiceRequestHandler(BaseHTTPRequestHandler):

    GET_ROUTES: Dict[str, Any] = {
        '/health-check': health_check,
        '/verify-email': verify_email,
        '/current-user': get_current_logged_user
    }

    POST_ROUTES: Dict[str, Any] = {
        '/register': register,
        '/login': authenticate
    }

    REQUEST_METHODS: Dict[str, Dict[str, Any]] = {
        'GET': GET_ROUTES,
        'POST': POST_ROUTES
    }

    PROTECTED_ROUTES = ['/current-user']

    def _request_handler(self) -> None:
        handler_dict: Dict[str, Any] = self.REQUEST_METHODS.get(
            self.command, {})
        parsed_path = urlparse(self.path)
        path = parsed_path.path

        if handler_dict is not None and path not in handler_dict:
            self._throw_exception(message='Not Found', code=404)
            return

        handler_method = handler_dict.get(path, None)

        if path in self.PROTECTED_ROUTES and not self._validate_token():
            return

        headers = {key: self.headers[key] for key in self.headers.keys()}
        query_params = parse_query_params(parsed_path.query)

        data = None
        if self.command == 'POST':
            if self.headers.get('Content-Type') != 'application/json':
                self._throw_exception(message='Unsupported Media Type',
                                      code=415)
                return

            content_length = int(self.headers['Content-Length'])
            body = self.rfile.read(content_length)
            try:
                data = json.loads(body.decode('utf-8'))
            except json.JSONDecodeError:
                self._throw_exception(
                    message='Invalid JSON format. Please check the JSON structure.', code=400)
                return

        with get_db() as db:
            response = argument_injector(handler_method)(headers=headers,
                                                         query_params=query_params,
                                                         db=db,
                                                         data=data)

        self._response_handler(response)

    def _validate_token(self) -> bool:
        token = self.headers.get('Authorization')
        if not token:
            self._throw_exception('Token is missing.', 401)
            return False
        try:
            decode_jwt(token)
            # self.headers.add_header('user-id', str())
        except jwt.ExpiredSignatureError:
            self._throw_exception('Token expired.', 401)
            return False
        except jwt.InvalidTokenError:
            self._throw_exception('Invalid token.', 401)
            return False
        return True

    def _response_handler(self, response: dict) -> None:
        self.send_response(response.get('status_code', 200))
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(response).encode())
        self.wfile.write(b'\n')

    def _throw_exception(self, message: str, code: int) -> None:
        body = {"message": message, 'status_code': code}
        self._response_handler(body)

    def do_GET(self) -> None:
        self._request_handler()

    def do_POST(self) -> None:
        self._request_handler()
