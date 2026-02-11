import asyncio
from my_sse.server import Server
from my_sse.http import Router, Request, SSEResponse


async def hello(request: Request):
    return {"message": "Hello, World!"}


async def counter(request: Request):
    for i in range(5):
        yield SSEResponse({"count": i})
        await asyncio.sleep(1)


async def main():
    routers = [
        Router("/hello", method="GET", endpoint=hello, is_sse=False),
        Router("/counter", method="GET", endpoint=counter, is_sse=True),
    ]

    server = Server(localhost="127.0.0.1", port=8000, routers=routers)

    await server.main()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nServer stopped")
