from enum import Enum


class ErrorType(str, Enum):
    AUTHENTICATION_ERROR = "authentication_error"
    BILLING_ERROR = "billing_error"
    INTERNAL_ERROR = "internal_error"
    INVALID_REQUEST_ERROR = "invalid_request_error"
    NOT_FOUND_ERROR = "not_found_error"
    PERMISSION_ERROR = "permission_error"
    RATE_LIMIT_ERROR = "rate_limit_error"
    UPSTREAM_ERROR = "upstream_error"
    VALIDATION_ERROR = "validation_error"
    VERTEX_SCHEMA_ERROR = "vertex_schema_error"

    def __str__(self) -> str:
        return str(self.value)
