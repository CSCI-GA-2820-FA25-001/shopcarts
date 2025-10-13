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

from wsgi import app
from service.common import error_handlers, status
from service.models import DataValidationError


class TestErrorHandlers(TestCase):
    """Unit tests for error handler helpers"""

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

    def test_request_validation_error_delegates_to_bad_request(self):
        """It should pass DataValidationError handling to bad_request"""
        error = DataValidationError("invalid payload")
        with patch("service.common.error_handlers.bad_request") as mock_bad_request:
            error_handlers.request_validation_error(error)
            mock_bad_request.assert_called_once_with(error)

    def test_bad_request_response_structure(self):
        """It should format a proper bad request response"""
        message = "invalid payload"
        with patch.object(error_handlers.app.logger, "warning") as mock_warning:
            response, status_code = error_handlers.bad_request(message)
            mock_warning.assert_called_once_with(message)

        data = response.get_json()
        self.assertEqual(status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(data["status"], status.HTTP_400_BAD_REQUEST)
        self.assertEqual(data["error"], "Bad Request")
        self.assertEqual(data["message"], message)

    def test_not_found_response_structure(self):
        """It should format a proper not found response"""
        message = "resource missing"
        with patch.object(error_handlers.app.logger, "warning") as mock_warning:
            response, status_code = error_handlers.not_found(message)
            mock_warning.assert_called_once_with(message)

        data = response.get_json()
        self.assertEqual(status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(data["status"], status.HTTP_404_NOT_FOUND)
        self.assertEqual(data["error"], "Not Found")
        self.assertEqual(data["message"], message)

    def test_method_not_supported_response_structure(self):
        """It should format a proper method not allowed response"""
        message = "PUT not allowed"
        with patch.object(error_handlers.app.logger, "warning") as mock_warning:
            response, status_code = error_handlers.method_not_supported(message)
            mock_warning.assert_called_once_with(message)

        data = response.get_json()
        self.assertEqual(status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
        self.assertEqual(data["status"], status.HTTP_405_METHOD_NOT_ALLOWED)
        self.assertEqual(data["error"], "Method not Allowed")
        self.assertEqual(data["message"], message)

    def test_mediatype_not_supported_response_structure(self):
        """It should format a proper unsupported media type response"""
        message = "text/plain unsupported"
        with patch.object(error_handlers.app.logger, "warning") as mock_warning:
            response, status_code = error_handlers.mediatype_not_supported(message)
            mock_warning.assert_called_once_with(message)

        data = response.get_json()
        self.assertEqual(status_code, status.HTTP_415_UNSUPPORTED_MEDIA_TYPE)
        self.assertEqual(data["status"], status.HTTP_415_UNSUPPORTED_MEDIA_TYPE)
        self.assertEqual(data["error"], "Unsupported media type")
        self.assertEqual(data["message"], message)

    def test_internal_server_error_response_structure(self):
        """It should format a proper internal server error response"""
        message = "unexpected failure"
        with patch.object(error_handlers.app.logger, "error") as mock_error:
            response, status_code = error_handlers.internal_server_error(message)
            mock_error.assert_called_once_with(message)

        data = response.get_json()
        self.assertEqual(status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)
        self.assertEqual(data["status"], status.HTTP_500_INTERNAL_SERVER_ERROR)
        self.assertEqual(data["error"], "Internal Server Error")
        self.assertEqual(data["message"], message)
