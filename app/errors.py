import logging
from typing import Any, Dict, Optional

from fastapi import FastAPI, HTTPException, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

HTTP_422_UNPROCESSABLE = getattr(status, "HTTP_422_UNPROCESSABLE_CONTENT", 422)
logger = logging.getLogger("app.error")

class ErrorCode:
    HTTP_ERROR = "HTTP_ERROR"
    VALIDATION_ERROR = "VALIDATION_ERROR"
    INTERNAL_SERVER_ERROR = "INTERNAL_SERVER_ERROR"
    NOT_AUTHENTICATED = "NOT_AUTHENTICATED"
    INVALID_TOKEN = "INVALID_TOKEN"
    INVALID_TOKEN_TYPE = "INVALID_TOKEN_TYPE"
    INVALID_TOKEN_SUBJECT = "INVALID_TOKEN_SUBJECT"
    FORBIDDEN = "FORBIDDEN"
    USER_NOT_FOUND = "USER_NOT_FOUND"
    USERNAME_ALREADY_EXISTS = "USERNAME_ALREADY_EXISTS"
    INVALID_CREDENTIALS = "INVALID_CREDENTIALS"
    INVALID_REFRESH_TOKEN = "INVALID_REFRESH_TOKEN"
    PROJECT_NOT_FOUND = "PROJECT_NOT_FOUND"
    PROJECT_MEMBER_NOT_FOUND = "PROJECT_MEMBER_NOT_FOUND"
    PROJECT_ALREADY_EXISTS = "PROJECT_ALREADY_EXISTS"
    ORGANIZATION_NOT_FOUND = "ORGANIZATION_NOT_FOUND"
    ORGANIZATION_MEMBER_NOT_FOUND = "ORGANIZATION_MEMBER_NOT_FOUND"
    PROJECT_ORGANIZATION_MISMATCH = "PROJECT_ORGANIZATION_MISMATCH"
    TEST_CASE_NOT_FOUND = "TEST_CASE_NOT_FOUND"
    TEST_CASE_ALREADY_EXISTS = "TEST_CASE_ALREADY_EXISTS"
    TEST_SUITE_NOT_FOUND = "TEST_SUITE_NOT_FOUND"
    TEST_SUITE_ALREADY_EXISTS = "TEST_SUITE_ALREADY_EXISTS"
    TEST_SUITE_CASE_NOT_FOUND = "TEST_SUITE_CASE_NOT_FOUND"
    ENVIRONMENT_NOT_FOUND = "ENVIRONMENT_NOT_FOUND"
    VARIABLE_NOT_FOUND = "VARIABLE_NOT_FOUND"
    BATCH_RUN_NOT_FOUND = "BATCH_RUN_NOT_FOUND"
    TEST_RUN_NOT_FOUND = "TEST_RUN_NOT_FOUND"
    WEB_TEST_CASE_NOT_FOUND = "WEB_TEST_CASE_NOT_FOUND"
    WEB_TEST_CASE_ALREADY_EXISTS = "WEB_TEST_CASE_ALREADY_EXISTS"
    WEB_TEST_RUN_NOT_FOUND = "WEB_TEST_RUN_NOT_FOUND"


DEFAULT_HTTP_ERROR_CODES = {
    status.HTTP_400_BAD_REQUEST: ErrorCode.HTTP_ERROR,
    status.HTTP_401_UNAUTHORIZED: ErrorCode.NOT_AUTHENTICATED,
    status.HTTP_403_FORBIDDEN: "FORBIDDEN",
    status.HTTP_404_NOT_FOUND: "NOT_FOUND",
    status.HTTP_405_METHOD_NOT_ALLOWED: "METHOD_NOT_ALLOWED",
    status.HTTP_409_CONFLICT: "CONFLICT",
    HTTP_422_UNPROCESSABLE: ErrorCode.VALIDATION_ERROR,
    status.HTTP_429_TOO_MANY_REQUESTS: "TOO_MANY_REQUESTS",
}


class AppException(Exception):
    def __init__(
        self,
        status_code: int,
        code: str,
        message: str,
        details: Optional[Any] = None,
    ) -> None:
        self.status_code = status_code
        self.code = code
        self.message = message
        self.details = details
        super().__init__(message)


def _request_id(request: Request) -> str:
    return getattr(request.state, "request_id", "-")


def _error_response(
    request: Request,
    status_code: int,
    code: str,
    message: str,
    details: Optional[Any] = None,
) -> JSONResponse:
    payload: Dict[str, Any] = {
        "success": False,
        "error": {
            "code": code,
            "message": message,
            "request_id": _request_id(request),
        },
        # Compatibility for existing frontend handlers.
        "detail": message,
    }
    if details is not None:
        payload["error"]["details"] = details
    return JSONResponse(status_code=status_code, content=payload)


async def app_exception_handler(request: Request, exc: AppException) -> JSONResponse:
    logger.warning(
        "app_exception",
        extra={
            "event": "app_exception",
            "request_id": _request_id(request),
            "status_code": exc.status_code,
            "path": request.url.path,
            "method": request.method,
            "code": exc.code,
        },
    )
    return _error_response(
        request=request,
        status_code=exc.status_code,
        code=exc.code,
        message=exc.message,
        details=exc.details,
    )


async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    message = exc.detail if isinstance(exc.detail, str) else "Request failed"
    code = DEFAULT_HTTP_ERROR_CODES.get(exc.status_code, ErrorCode.HTTP_ERROR)
    details = None if isinstance(exc.detail, str) else exc.detail
    logger.warning(
        "http_exception",
        extra={
            "event": "http_exception",
            "request_id": _request_id(request),
            "status_code": exc.status_code,
            "path": request.url.path,
            "method": request.method,
            "code": code,
        },
    )
    return _error_response(
        request=request,
        status_code=exc.status_code,
        code=code,
        message=message,
        details=details,
    )


async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    logger.warning(
        "validation_exception",
        extra={
            "event": "validation_exception",
            "request_id": _request_id(request),
            "status_code": HTTP_422_UNPROCESSABLE,
            "path": request.url.path,
            "method": request.method,
            "code": ErrorCode.VALIDATION_ERROR,
        },
    )
    return _error_response(
        request=request,
        status_code=HTTP_422_UNPROCESSABLE,
        code=ErrorCode.VALIDATION_ERROR,
        message="Validation failed",
        details=exc.errors(),
    )


async def unhandled_exception_handler(request: Request, _exc: Exception) -> JSONResponse:
    logger.exception(
        "unhandled_exception",
        extra={
            "event": "unhandled_exception",
            "request_id": _request_id(request),
            "status_code": status.HTTP_500_INTERNAL_SERVER_ERROR,
            "path": request.url.path,
            "method": request.method,
            "code": ErrorCode.INTERNAL_SERVER_ERROR,
        },
    )
    return _error_response(
        request=request,
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        code=ErrorCode.INTERNAL_SERVER_ERROR,
        message="Internal server error",
    )


def register_exception_handlers(app: FastAPI) -> None:
    app.add_exception_handler(AppException, app_exception_handler)
    app.add_exception_handler(HTTPException, http_exception_handler)
    app.add_exception_handler(StarletteHTTPException, http_exception_handler)
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(Exception, unhandled_exception_handler)
