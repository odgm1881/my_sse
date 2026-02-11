from infrastructure.exceptions import HTTPException, BadRequest
from infrastructure.http import Router, Request
from infrastructure.http_formatter import CreateResponse, response_to_http_sse


import asyncio


class Server:
    def __init__(
        self,
        localhost: str,
        port: int,
        routers: list[Router],
    ) -> None:
        self.localhost = localhost
        self.port = port
        self.routers = routers

    async def handle_client(
        self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter
    ) -> None:
        try:
            while True:
                data = await reader.read(8192)

                try:
                    request = self.to_request(data)
                except BadRequest as e:
                    response = CreateResponse(400)(e.details)
                    writer.write(response)
                    await writer.drain()
                    break
                except (IndexError, KeyError) as e:
                    response = CreateResponse(400)(f"Malformed request: {e}")
                    writer.write(response)
                    await writer.drain()
                    break

                router = self.find_router(request)

                if not router:
                    response = CreateResponse(404)()
                    writer.write(response)
                    await writer.drain()
                    continue

                request.path_params = router.match(request.url)

                if not router.is_sse:
                    try:
                        result = await router.endpoint(request)
                        response = CreateResponse(200)(result)
                    except HTTPException as e:
                        response = CreateResponse(e.status_code)(e.details)
                    except Exception as e:
                        response = CreateResponse(500)(str(e))

                    writer.write(response)
                    await writer.drain()
                    continue

                # SSE endpoint
                try:
                    initial_response = response_to_http_sse()
                    writer.write(initial_response)
                    await writer.drain()

                    async for event_data in router.endpoint(request):
                        event_bytes = event_data.to_bytes()

                        if len(event_bytes) == 0:
                            break

                        sse_message = b"data: " + event_bytes + b"\n\n"
                        chunk_size = hex(len(sse_message))[2:]

                        writer.write(
                            f"{chunk_size}\r\n".encode() + sse_message + b"\r\n"
                        )
                        await writer.drain()

                    writer.write(b"0\r\n\r\n")
                    await writer.drain()
                except Exception as e:
                    print(f"SSE Error: {e}")
                    writer.write(b"0\r\n\r\n")
                    await writer.drain()

                break

        except Exception as e:
            print(f"Critical error in handle_client: {e}")
        finally:
            writer.close()
            await writer.wait_closed()

    def find_router(self, request: Request) -> Router | None:
        for router in self.routers:
            if router.method != request.method:
                continue

            if router.match(request.url) is not None:
                return router

        return None

    def to_request(self, data: bytes) -> Request:
        if not data:
            raise BadRequest("Empty request data")

        try:
            lines = data.decode("utf-8").split("\r\n")
        except UnicodeDecodeError as e:
            raise BadRequest(f"Invalid UTF-8 encoding: {e}")

        if not lines or len(lines) == 0:
            raise BadRequest("Invalid HTTP request format")

        request_line = lines[0].split(" ")

        if len(request_line) < 3:
            raise BadRequest(f"Invalid request line: {lines[0]}")

        method = request_line[0]
        full_url = request_line[1]

        if "?" in full_url:
            url, query_string = full_url.split("?", 1)
            query = {}
            for param in query_string.split("&"):
                if "=" in param:
                    key, value = param.split("=", 1)
                    query[key] = value
        else:
            url = full_url
            query = None

        headers = {}
        body_start = 0
        for i, line in enumerate(lines[1:], 1):
            if line == "":
                body_start = i + 1
                break
            if ":" in line:
                key, value = line.split(":", 1)
                headers[key.strip()] = value.strip()

        body = None
        if body_start < len(lines):
            body_text = "\r\n".join(lines[body_start:])
            if body_text:
                body = body_text

        return Request(
            method=method,
            url=url,
            query=query,
            content_length=int(headers.get("Content-Length", 0))
            if "Content-Length" in headers
            else None,
            content_type=headers.get("Content-Type"),
            body=body,
        )

    async def main(self) -> None:
        server = await asyncio.start_server(
            self.handle_client, self.localhost, self.port
        )

        async with server:
            await server.serve_forever()
