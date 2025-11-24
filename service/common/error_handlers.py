######################################################################
# Copyright 2016, 2024 John J. Rofrano. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
######################################################################
"""
Module: error_handlers
"""

from flask import jsonify
from flask import current_app as app  # Import Flask application
from werkzeug.exceptions import HTTPException
from service.models import DataValidationError
from . import status
from service.routes import api

######################################################################
# Helpers
######################################################################
_STATUS_NAME_MAP = {
    getattr(status, name): " ".join(name.split("_")[2:]).title()
    for name in dir(status)
    if name.startswith("HTTP_")
}


def _make_error_payload(error) -> tuple[dict, int]:
    """Normalize different error types into a JSON-friendly payload."""
    code = status.HTTP_500_INTERNAL_SERVER_ERROR
    message = ""

    # Tuples/lists in the form (status_code, message)
    if isinstance(error, (tuple, list)):
        if len(error) > 0 and isinstance(error[0], int):
            code = error[0]
        if len(error) > 1 and isinstance(error[1], str):
            message = error[1]

    # HTTPExceptions (typically from abort())
    elif isinstance(error, HTTPException):
        code = getattr(error, "code", status.HTTP_500_INTERNAL_SERVER_ERROR)
        # Prefer the Werkzeug description; fall back to string form
        description = getattr(error, "description", "") or ""
        message = description or str(error)

    # Any other exception or error object
    else:
        code = getattr(error, "code", status.HTTP_500_INTERNAL_SERVER_ERROR)
        if error is not None:
            message = str(error)

    js = {
        "status": code,
        "error": _STATUS_NAME_MAP.get(code, "Unknown"),
        "message": message,
    }
    return js, code


def _handle(error, is_api: bool):
    js, code = _make_error_payload(error)
    logger = app.logger.error if js["status"] >= 500 else app.logger.warning
    logger(js["message"])
    return (js, code) if is_api else (jsonify(js), code)


######################################################################
# Flask App Error Handlers
######################################################################
@app.errorhandler(DataValidationError)
def request_validation_error(error):
    """Handles data validation errors as 400s"""
    return _handle((status.HTTP_400_BAD_REQUEST, str(error)), False)


@app.errorhandler(HTTPException)
def handle_http_exception(error):
    """Handle all HTTPExceptions"""
    return _handle(error, False)


@app.errorhandler(Exception)
def internal_server_error(error):
    """Handles unexpected server errors"""
    return _handle((status.HTTP_500_INTERNAL_SERVER_ERROR, str(error)), False)


######################################################################
# Flask-RESTX Error Handlers
######################################################################
@api.errorhandler(DataValidationError)
def api_request_validation_error(error):
    """RESTX handler for data validation errors"""
    return _handle((status.HTTP_400_BAD_REQUEST, str(error)), True)


@api.errorhandler(HTTPException)
def api_handle_http_exception(error):
    """RESTX handler for HTTPExceptions"""
    return _handle(error, True)


@api.errorhandler(Exception)
def api_internal_server_error(error):
    """RESTX handler for unexpected server errors"""
    return _handle((status.HTTP_500_INTERNAL_SERVER_ERROR, str(error)), True)
