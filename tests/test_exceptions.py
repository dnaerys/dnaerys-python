"""Tests for dnaerys._exceptions — exception hierarchy and warning class."""

from dnaerys._exceptions import (
    DnaerysAuthenticationError,
    DnaerysConnectionError,
    DnaerysError,
    DnaerysIncompleteResultWarning,
    DnaerysInvalidRequestError,
    DnaerysNotFoundError,
    DnaerysResourceExhausted,
    DnaerysServerError,
)


# -----------------------------------------------------------------------
# Subclass relationships
# -----------------------------------------------------------------------


class TestExceptionHierarchy:
    def test_dnaerys_error_is_exception(self):
        assert issubclass(DnaerysError, Exception)

    def test_connection_error_is_dnaerys_error(self):
        assert issubclass(DnaerysConnectionError, DnaerysError)

    def test_authentication_error_is_dnaerys_error(self):
        assert issubclass(DnaerysAuthenticationError, DnaerysError)

    def test_not_found_error_is_dnaerys_error(self):
        assert issubclass(DnaerysNotFoundError, DnaerysError)

    def test_invalid_request_error_is_dnaerys_error(self):
        assert issubclass(DnaerysInvalidRequestError, DnaerysError)

    def test_server_error_is_dnaerys_error(self):
        assert issubclass(DnaerysServerError, DnaerysError)

    def test_resource_exhausted_is_dnaerys_error(self):
        assert issubclass(DnaerysResourceExhausted, DnaerysError)


# -----------------------------------------------------------------------
# is_retryable property
# -----------------------------------------------------------------------


class TestIsRetryable:
    def test_connection_error_is_retryable(self):
        assert DnaerysConnectionError("timeout").is_retryable is True

    def test_resource_exhausted_is_retryable(self):
        assert DnaerysResourceExhausted("rate limit").is_retryable is True

    def test_authentication_error_not_retryable(self):
        assert DnaerysAuthenticationError("bad creds").is_retryable is False

    def test_not_found_error_not_retryable(self):
        assert DnaerysNotFoundError("no such thing").is_retryable is False

    def test_invalid_request_error_not_retryable(self):
        assert DnaerysInvalidRequestError("bad arg").is_retryable is False

    def test_server_error_not_retryable(self):
        assert DnaerysServerError("internal").is_retryable is False

    def test_base_error_not_retryable(self):
        assert DnaerysError().is_retryable is False


# -----------------------------------------------------------------------
# Warning class
# -----------------------------------------------------------------------


class TestWarning:
    def test_incomplete_result_warning_is_user_warning(self):
        assert issubclass(DnaerysIncompleteResultWarning, UserWarning)


# -----------------------------------------------------------------------
# Error message preservation
# -----------------------------------------------------------------------


class TestErrorMessage:
    def test_error_message_preserved(self):
        err = DnaerysConnectionError("timeout")
        assert err.args[0] == "timeout"
