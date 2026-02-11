# My SSE Server

Simple HTTP server with Server-Sent Events support. Built with asyncio, no dependencies.

## Features

- ✨ Pure Python implementation (no external web frameworks)
- 🚀 Async/await based on asyncio
- 📡 Server-Sent Events (SSE) support
- 🛣️ URL routing with path parameters (`/users/{id}`)
- ❓ Query string parsing
- 🔥 HTTP exception handling
- 📦 Chunked transfer encoding for SSE

## Quick Start

```python
import asyncio
from my_sse.server import Server
from my_sse.http import Router, Request, SSEResponse

# Regular endpoint
async def hello(request: Request):
    return {"message": "Hello, World!"}

# SSE endpoint
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
```

## Requirements

- Python 3.10+ (for match/case syntax and union type hints)

## Installation

```bash
git clone https://github.com/yourusername/my_sse.git
cd my_sse
python main.py
```

## Testing

**Regular endpoint:**
```bash
curl http://127.0.0.1:8000/hello
```

**SSE endpoint:**
```bash
curl -N http://127.0.0.1:8000/counter
```

**Browser (SSE):**
```javascript
const es = new EventSource('http://127.0.0.1:8000/counter');
es.onmessage = (e) => console.log(e.data);
```

## Project Structure

```
my_sse/
├── my_sse/
│   ├── exceptions.py      # HTTP exceptions
│   ├── http.py            # Request, Response, Router, SSEResponse
│   ├── http_formatter.py  # HTTP response formatting
│   └── server.py          # Core server implementation
├── main.py                # Example application
└── requirements.txt       # Dependencies (none required)
```

## License

MIT License - see [LICENSE](LICENSE) file for details.
