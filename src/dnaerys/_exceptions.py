"""Exception hierarchy and warning class for the Dnaerys client library.

Each exception maps to a group of gRPC status codes (see the table below).
The ``is_retryable`` property indicates whether the error is transient and
the same request may succeed if retried.

::

    DnaerysError (base)                       is_retryable = False
    +-- DnaerysConnectionError                is_retryable = True
    |       UNAVAILABLE, DEADLINE_EXCEEDED
    +-- DnaerysAuthenticationError             is_retryable = False
    |       UNAUTHENTICATED, PERMISSION_DENIED
    +-- DnaerysNotFoundError                   is_retryable = False
    |       NOT_FOUND
    +-- DnaerysInvalidRequestError             is_retryable = False
    |       INVALID_ARGUMENT, FAILED_PRECONDITION, OUT_OF_RANGE
    +-- DnaerysServerError                     is_retryable = False
    |       INTERNAL, UNKNOWN, DATA_LOSS, UNIMPLEMENTED
    +-- DnaerysResourceExhausted               is_retryable = True
            RESOURCE_EXHAUSTED

    DnaerysIncompleteResultWarning (UserWarning, not part of error hierarchy)
        Emitted when affected=True in a server response.

The ``raise_for_grpc_error`` function maps gRPC status codes to the
appropriate exception subclass.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, NoReturn

if TYPE_CHECKING:
    import grpc

__all__ = [
    "DnaerysError",
    "DnaerysConnectionError",
    "DnaerysAuthenticationError",
    "DnaerysNotFoundError",
    "DnaerysInvalidRequestError",
    "DnaerysServerError",
    "DnaerysResourceExhausted",
    "DnaerysIncompleteResultWarning",
    "raise_for_grpc_error",
]


class DnaerysError(Exception):
    """Base exception for all Dnaerys client errors.

    All Dnaerys-specific exceptions inherit from this class, so
    ``except DnaerysError`` catches any library error.

    The ``is_retryable`` property indicates whether the same request may
    succeed if retried.  The base class returns ``False``; subclasses
    override as appropriate.
    """

    @property
    def is_retryable(self) -> bool:
        """Whether this error is transient and the request may be retried."""
        return False


class DnaerysConnectionError(DnaerysError):
    """Connection failure or timeout.

    Raised when the gRPC channel cannot reach the server (``UNAVAILABLE``)
    or a deadline is exceeded (``DEADLINE_EXCEEDED``).  These are transient
    errors — retrying (possibly with a longer timeout) may succeed.
    """

    @property
    def is_retryable(self) -> bool:
        """Returns ``True`` — connection errors are transient."""
        return True


class DnaerysAuthenticationError(DnaerysError):
    """Authentication or authorization failure.

    Raised for ``UNAUTHENTICATED`` (missing/invalid credentials) or
    ``PERMISSION_DENIED`` (valid credentials but insufficient permissions).
    Not retryable — the credentials or permissions must be fixed.
    """


class DnaerysNotFoundError(DnaerysError):
    """Requested resource not found.

    Raised for ``NOT_FOUND`` gRPC status.  Not retryable — the resource
    does not exist.
    """


class DnaerysInvalidRequestError(DnaerysError):
    """Invalid request parameters.

    Raised for ``INVALID_ARGUMENT``, ``FAILED_PRECONDITION``, or
    ``OUT_OF_RANGE`` gRPC status codes.  Not retryable — the request
    must be corrected.
    """


class DnaerysServerError(DnaerysError):
    """Server-side error.

    Raised for ``INTERNAL``, ``UNKNOWN``, ``DATA_LOSS``, or
    ``UNIMPLEMENTED`` gRPC status codes.  Not retryable by default —
    the cause is on the server side and may require investigation.
    """


class DnaerysResourceExhausted(DnaerysError):
    """Resource exhausted (rate limit, quota, memory).

    Raised for ``RESOURCE_EXHAUSTED`` gRPC status.  Retryable after
    a backoff period.
    """

    @property
    def is_retryable(self) -> bool:
        """Returns ``True`` — may succeed after backoff."""
        return True


class DnaerysIncompleteResultWarning(UserWarning):
    """Warning emitted when results may be incomplete due to unreachable cluster nodes.

    This warning fires when a server response has ``affected=True``,
    indicating that cluster nodes holding potentially relevant data were
    unreachable.  The results are still usable but may be incomplete.

    Suppress with ``warnings.filterwarnings("ignore", category=DnaerysIncompleteResultWarning)``.
    """


def raise_for_grpc_error(error: grpc.RpcError) -> NoReturn:
    """Map a gRPC ``RpcError`` to the appropriate ``DnaerysError`` subclass and raise it.

    The original gRPC error is chained via ``raise ... from error`` so power
    users can inspect the raw status code and details.

    Parameters
    ----------
    error : grpc.RpcError
        The gRPC error caught during a stub call or stream iteration.

    Raises
    ------
    DnaerysConnectionError
        For ``UNAVAILABLE`` or ``DEADLINE_EXCEEDED``.
    DnaerysAuthenticationError
        For ``UNAUTHENTICATED`` or ``PERMISSION_DENIED``.
    DnaerysNotFoundError
        For ``NOT_FOUND``.
    DnaerysInvalidRequestError
        For ``INVALID_ARGUMENT``, ``FAILED_PRECONDITION``, or ``OUT_OF_RANGE``.
    DnaerysResourceExhausted
        For ``RESOURCE_EXHAUSTED``.
    DnaerysServerError
        For ``INTERNAL``, ``UNKNOWN``, ``DATA_LOSS``, ``UNIMPLEMENTED``,
        or any unmapped status code.
    """
    import grpc as _grpc

    _GRPC_CODE_MAP: dict[_grpc.StatusCode, type[DnaerysError]] = {
        _grpc.StatusCode.UNAVAILABLE: DnaerysConnectionError,
        _grpc.StatusCode.DEADLINE_EXCEEDED: DnaerysConnectionError,
        _grpc.StatusCode.UNAUTHENTICATED: DnaerysAuthenticationError,
        _grpc.StatusCode.PERMISSION_DENIED: DnaerysAuthenticationError,
        _grpc.StatusCode.NOT_FOUND: DnaerysNotFoundError,
        _grpc.StatusCode.INVALID_ARGUMENT: DnaerysInvalidRequestError,
        _grpc.StatusCode.FAILED_PRECONDITION: DnaerysInvalidRequestError,
        _grpc.StatusCode.OUT_OF_RANGE: DnaerysInvalidRequestError,
        _grpc.StatusCode.RESOURCE_EXHAUSTED: DnaerysResourceExhausted,
        _grpc.StatusCode.INTERNAL: DnaerysServerError,
        _grpc.StatusCode.UNKNOWN: DnaerysServerError,
        _grpc.StatusCode.DATA_LOSS: DnaerysServerError,
        _grpc.StatusCode.UNIMPLEMENTED: DnaerysServerError,
    }

    code = error.code()
    details = error.details()
    exc_cls = _GRPC_CODE_MAP.get(code, DnaerysServerError)
    raise exc_cls(details) from error
