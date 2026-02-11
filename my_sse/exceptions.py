# HTTP Exceptions
class HTTPException(Exception):
    def __init__(self, status_code: int, message: str, details: str = ""):
        self.status_code = status_code
        self.message = message
        self.details = details
        super().__init__(
            f"{status_code} {message}: {details}"
            if details
            else f"{status_code} {message}"
        )


class BadRequest(HTTPException):
    """400 Bad Request"""

    def __init__(self, details: str = ""):
        super().__init__(400, "Bad Request", details)


class NotFound(HTTPException):
    """404 Not Found"""

    def __init__(self, details: str = ""):
        super().__init__(404, "Not Found", details)


class RequestTimeout(HTTPException):
    """408 Request Timeout"""

    def __init__(self, details: str = ""):
        super().__init__(408, "Request Timeout", details)


class TooManyRequests(HTTPException):
    """429 Too Many Requests"""

    def __init__(self, details: str = ""):
        super().__init__(429, "Too Many Requests", details)


class InternalServerError(HTTPException):
    """500 Internal Server Error"""

    def __init__(self, details: str = ""):
        super().__init__(500, "Internal Server Error", details)


class GatewayTimeout(HTTPException):
    """504 Gateway Timeout"""

    def __init__(self, details: str = ""):
        super().__init__(504, "Gateway Timeout", details)
