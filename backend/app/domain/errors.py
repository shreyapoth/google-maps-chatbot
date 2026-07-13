from __future__ import annotations


class ApplicationError(Exception):
    def __init__(self, code: str, message: str, context: dict | None = None):
        self.code = code
        self.message = message
        self.context = context or {}
        super().__init__(message)


class ExternalServiceError(ApplicationError):
    pass


class ExternalAuthenticationError(ExternalServiceError):
    pass


class ExternalPermissionError(ExternalServiceError):
    pass


class ExternalRateLimitError(ExternalServiceError):
    pass


class ExternalTimeoutError(ExternalServiceError):
    pass


class ExternalResponseError(ExternalServiceError):
    pass
