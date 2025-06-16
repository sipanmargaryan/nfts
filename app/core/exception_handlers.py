from fastapi import Request
from fastapi.exceptions import RequestValidationError
from starlette.status import HTTP_422_UNPROCESSABLE_ENTITY

from .exceptions import MethodNotAllowed, NotFound, ServiceException, ValidationError


async def not_found_handler(request: Request, exc: NotFound):
    return exc.to_response()


async def service_exception_handler(request: Request, exc: ServiceException):
    return exc.to_response()


async def method_not_allowed_handler(request: Request, exc: MethodNotAllowed):
    return exc.to_response()


async def validation_error_handler(request: Request, exc: RequestValidationError):
    return ValidationError(status_code=HTTP_422_UNPROCESSABLE_ENTITY).to_response()


def register_exception_handlers(app):
    app.add_exception_handler(NotFound, not_found_handler)
    app.add_exception_handler(ServiceException, service_exception_handler)
    app.add_exception_handler(MethodNotAllowed, method_not_allowed_handler)
    app.add_exception_handler(RequestValidationError, validation_error_handler)
