# Overview

HTTP protocol utilities including client abstractions, coroutine-style server implementations, ASGI support, and
various HTTP-related tools. Emphasizes sans-io/coroutine approaches for framework-agnostic code.

# Key Components

- **[clients](https://github.com/wrmsr/omlish/blob/master/omlish/http/clients)** - HTTP client abstraction:
  - Unified interface over urllib and httpx backends.
  - Sync and async client support.
  - Pluggable backend implementations.
- **[coro](https://github.com/wrmsr/omlish/blob/master/omlish/http/coro)** - Coroutine/sans-io HTTP server:
  - Reformulation of stdlib `http.server` in coroutine style.
  - Works in sync, async, or any event loop context.
  - No thread/event loop dependencies, suitable for process supervisors.
- **[flasky](https://github.com/wrmsr/omlish/blob/master/omlish/http/flasky)** - Flask-style utilities and helpers.
- **asgi** - ASGI (Asynchronous Server Gateway Interface) utilities.
- **cookies** - HTTP cookie parsing and generation.
- **handlers** - HTTP request handlers.
- **headers** - HTTP header parsing and manipulation.
- **json** - JSON HTTP request/response utilities.
- **jwt** - JSON Web Token (JWT) support.
- **parsing** - HTTP message parsing.
- **sessions** - HTTP session management.
- **sse** - Server-Sent Events (SSE) support.
- **urls** - URL parsing and manipulation.

# Notable Modules

- **[clients/abc](https://github.com/wrmsr/omlish/blob/master/omlish/http/clients/abc.py)** - `HttpClient` interface
  with sync and async variants.
- **[clients/urllib](https://github.com/wrmsr/omlish/blob/master/omlish/http/clients/urllib.py)** - urllib-based client
  implementation.
- **[clients/httpx](https://github.com/wrmsr/omlish/blob/master/omlish/http/clients/httpx.py)** - httpx-based client
  implementation (optional dependency).
- **[coro](https://github.com/wrmsr/omlish/blob/master/omlish/http/coro)** - Sans-io HTTP server machinery extracted
  from stdlib.
- **[asgi](https://github.com/wrmsr/omlish/blob/master/omlish/http/asgi.py)** - ASGI application and middleware
  support.
- **[cookies](https://github.com/wrmsr/omlish/blob/master/omlish/http/cookies.py)** - Cookie parsing and serialization.
- **[headers](https://github.com/wrmsr/omlish/blob/master/omlish/http/headers.py)** - Header manipulation utilities.
- **[json](https://github.com/wrmsr/omlish/blob/master/omlish/http/json.py)** - JSON request/response helpers.
- **[jwt](https://github.com/wrmsr/omlish/blob/master/omlish/http/jwt.py)** - JWT encoding/decoding.
- **[sse](https://github.com/wrmsr/omlish/blob/master/omlish/http/sse.py)** - Server-Sent Events implementation.
- **[urls](https://github.com/wrmsr/omlish/blob/master/omlish/http/urls.py)** - URL parsing and building.

# Example Usage

```python
from omlish.http import clients

# Abstract HTTP client (uses urllib or httpx)
client = clients.get_default_http_client()
response = client.request('GET', 'https://example.com')
print(response.text)

# Async client
async_client = clients.get_default_async_http_client()
response = await async_client.request('GET', 'https://example.com')
```

# Design Philosophy

The HTTP package emphasizes:
- **Sans-io/coroutine style** - Separate protocol logic from IO, enabling reuse across sync/async/other contexts.
- **Backend abstraction** - Abstract over urllib/httpx/other clients with a unified interface.
- **Framework compatibility** - Work with ASGI, WSGI, and custom frameworks.
- **Stdlib reformulation** - Extract and modernize useful stdlib HTTP code (like `http.server`) in coroutine style.

The coroutine-style server code is particularly valuable for process supervisors and other contexts where
asyncio/threading is unsuitable (see `omlish.io.fdio` for the event loop used with this code).
