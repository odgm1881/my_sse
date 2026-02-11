import json

from my_sse.http import Response, StatusCode


def response_to_http_sse() -> bytes:
    lines = [
        "HTTP/1.1 200 OK",
        "Content-Type: text/event-stream",
        "Cache-Control: no-cache",
        "Connection: keep-alive",
        "Transfer-Encoding: chunked",
        "",
        "",
    ]

    return "\r\n".join(lines).encode()


def response_to_http(response: Response) -> bytes:
    lines = [f"HTTP/1.1 {response.status.num_stat} {response.status.msg_stat}"]

    if response.content_type:
        lines.append(f"Content-Type: {response.content_type}")

    lines.append(f"Connection: {response.connection}")

    body_length = len(response.body) if response.body else 0
    lines.append(f"Content-Length: {body_length}")

    lines.append("")

    http_header = "\r\n".join(lines).encode()

    if response.body:
        return http_header + b"\r\n" + response.body

    return http_header + b"\r\n"


class CreateResponse:
    def __init__(self, num_status: int) -> None:
        self.num_status = num_status

    def __call__(self, *args, **kwds):
        create_table_status = {
            504: self.create_timeout_response,
            500: self.create_internal_error_response,
            429: self.create_too_many_requests_response,
            408: self.create_request_timeout_response,
            404: self.create_not_found_response,
            400: self.create_bad_request_response,
            200: self.create_success_response,
        }

        if self.num_status not in create_table_status.keys():
            return None

        return create_table_status[self.num_status](*args, **kwds)

    def create_not_found_response(self, error: str = "") -> bytes:
        return self.create_error_response(404, "Not Found", error_details=error)

    def create_bad_request_response(self, error: str = "") -> bytes:
        return self.create_error_response(400, "Bad Request", error_details=error)

    def create_request_timeout_response(self, error: str = "") -> bytes:
        return self.create_error_response(408, "Request Timeout", error_details=error)

    def create_too_many_requests_response(self, error: str = "") -> bytes:
        return self.create_error_response(429, "Too Many Requests", error_details=error)

    def create_internal_error_response(self, error: str = "") -> bytes:
        return self.create_error_response(
            500, "Internal Server Error", error_details=error
        )

    def create_timeout_response(self, error: str = "") -> bytes:
        return self.create_error_response(504, "Gateway Timeout", error_details=error)

    @staticmethod
    def create_error_response(
        status: int, message: str, error_details: str = ""
    ) -> bytes:
        body = f"{message}: {error_details}" if error_details else message
        return response_to_http(
            Response(
                status=StatusCode(status, message),
                connection="close",
                content_type="text/plain",
                body=body.encode(),
            )
        )

    @staticmethod
    def create_success_response(data) -> bytes:
        match data:
            case dict() | list():
                content_type = "application/json"
                body = json.dumps(data).encode("utf-8")
            case bytes():
                content_type = "application/octet-stream"
                body = data
            case str():
                content_type = "text/plain"
                body = data.encode("utf-8")
            case None:
                content_type = "text/plain"
                body = b""
            case _:
                # int, float, bool, и т.д.
                content_type = "text/plain"
                body = str(data).encode("utf-8")

        return response_to_http(
            Response(
                status=StatusCode(200, "OK"),
                connection="keep-alive",
                content_type=content_type,
                body=body,
            )
        )
