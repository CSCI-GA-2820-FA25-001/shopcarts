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
Common error handler tests
"""

from unittest import TestCase
from unittest.mock import patch

from werkzeug.exceptions import NotFound

from wsgi import app
from service.common import error_handlers, status
from service.models import DataValidationError


class TestErrorHandlers(TestCase):
    """Unit tests for error handler behavior"""

    @classmethod
    def setUpClass(cls):
        """Create and push an application context once for all tests"""
        cls.app = app
        cls.app_context = cls.app.app_context()
        cls.app_context.push()

    @classmethod
    def tearDownClass(cls):
        """Pop the shared application context"""
        cls.app_context.pop()

    def test_request_validation_error_returns_bad_request(self):
        """DataValidationError should be rendered as a 400 with details"""
        error = DataValidationError("invalid payload")
        with patch.object(error_handlers.app.logger, "warning") as mock_warning:
            response, status_code = error_handlers.request_validation_error(error)

        mock_warning.assert_called_once_with("invalid payload")
        data = response.get_json()
        self.assertEqual(status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(data["status"], status.HTTP_400_BAD_REQUEST)
        self.assertEqual(data["error"], "Bad Request")
        self.assertEqual(data["message"], "invalid payload")

    def test_handle_http_exception_uses_description(self):
        """HTTPExceptions should use their description as the message"""
        http_error = NotFound(description="resource missing")
        with patch.object(error_handlers.app.logger, "warning") as mock_warning:
            response, status_code = error_handlers.handle_http_exception(http_error)

        mock_warning.assert_called_once_with("resource missing")
        data = response.get_json()
        self.assertEqual(status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(data["status"], status.HTTP_404_NOT_FOUND)
        self.assertEqual(data["error"], "Not Found")
        self.assertEqual(data["message"], "resource missing")

    def test_internal_server_error_response_structure(self):
        """Unexpected errors should return a 500 with the original message"""
        message = "unexpected failure"
        with patch.object(error_handlers.app.logger, "error") as mock_error:
            response, status_code = error_handlers.internal_server_error(message)

        mock_error.assert_called_once_with(message)
        data = response.get_json()
        self.assertEqual(status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)
        self.assertEqual(data["status"], status.HTTP_500_INTERNAL_SERVER_ERROR)
        self.assertEqual(data["error"], "Internal Server Error")
        self.assertEqual(data["message"], message)

    def test_api_request_validation_error_returns_json(self):
        """RESTX DataValidationError handler should return a JSON payload"""
        error = DataValidationError("invalid payload")
        with patch.object(error_handlers.app.logger, "warning") as mock_warning:
            payload, status_code = error_handlers.api_request_validation_error(error)

        mock_warning.assert_called_once_with("invalid payload")
        self.assertIsInstance(payload, dict)
        self.assertEqual(status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(payload["status"], status.HTTP_400_BAD_REQUEST)
        self.assertEqual(payload["error"], "Bad Request")
        self.assertEqual(payload["message"], "invalid payload")

    def test_api_internal_server_error_returns_json(self):
        """RESTX 500 handler should return a JSON payload"""
        message = "unexpected failure"
        with patch.object(error_handlers.app.logger, "error") as mock_error:
            payload, status_code = error_handlers.api_internal_server_error(message)

        mock_error.assert_called_once_with(message)
        self.assertIsInstance(payload, dict)
        self.assertEqual(status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)
        self.assertEqual(payload["status"], status.HTTP_500_INTERNAL_SERVER_ERROR)
        self.assertEqual(payload["error"], "Internal Server Error")
        self.assertEqual(payload["message"], message)

    def test_make_error_payload_for_generic_exception(self):
        """Generic exceptions should fall back to 500 with str(error)"""
        error = ValueError("boom")
        payload, code = error_handlers._make_error_payload(error)

        self.assertEqual(code, status.HTTP_500_INTERNAL_SERVER_ERROR)
        self.assertEqual(payload["status"], status.HTTP_500_INTERNAL_SERVER_ERROR)
        self.assertEqual(payload["error"], "Internal Server Error")
        self.assertEqual(payload["message"], "boom")
