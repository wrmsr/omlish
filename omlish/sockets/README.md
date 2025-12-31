# Overview

Socket utilities for network programming including address handling, port allocation, server abstractions, and socket
IO utilities.

# Key Features

- **Address handling** - Parse and manipulate socket addresses (IPv4, IPv6, Unix domain sockets).
- **Port allocation** - Find and bind available ports.
- **Socket binding** - Utilities for binding sockets with proper error handling.
- **Server abstractions** - Base classes for socket servers.
- **Socket handlers** - Request handler abstractions for servers.
- **Wait utilities** - Wait for sockets to become available or ready.
- **Socket IO** - Read/write utilities for socket communication.

# Notable Modules

- **[addresses](https://github.com/wrmsr/omlish/blob/master/omlish/sockets/addresses.py)** - Socket address parsing and
  manipulation.
- **[ports](https://github.com/wrmsr/omlish/blob/master/omlish/sockets/ports.py)** - Port allocation and availability
  checking.
- **[bind](https://github.com/wrmsr/omlish/blob/master/omlish/sockets/bind.py)** - Socket binding utilities.
- **[server](https://github.com/wrmsr/omlish/blob/master/omlish/sockets/server)** - Socket server base classes and
  implementations.
- **[handlers](https://github.com/wrmsr/omlish/blob/master/omlish/sockets/handlers.py)** - Request handler
  abstractions.
- **[wait](https://github.com/wrmsr/omlish/blob/master/omlish/sockets/wait.py)** - Wait for socket conditions.
- **[io](https://github.com/wrmsr/omlish/blob/master/omlish/sockets/io.py)** - Socket IO utilities.

# Example Usage

```python
from omlish.sockets import ports

# Find an available port
port = ports.find_free_port()
print(f"Using port {port}")

# Check if port is in use
if ports.is_port_in_use(8080):
    print("Port 8080 is already in use")

# Bind to an address
from omlish.sockets import bind
sock = bind.bind_socket(('localhost', port))

# Wait for socket to be ready
from omlish.sockets import wait
wait.wait_for_socket(('localhost', 8080), timeout=30)
```

# Design Philosophy

Socket utilities should:
- **Handle edge cases** - Port already in use, address not available, timeout conditions.
- **Be cross-platform** - Work on Linux, macOS, and where possible Windows.
- **Provide good defaults** - Make common cases easy while allowing customization.
- **Be testable** - Make it easy to write tests that use sockets without conflicts.

These utilities are used throughout the codebase for:
- Network servers (`omlish.http.coro`)
- Service startup (`omlish.daemons`)
- Testing (finding free ports for test services)
- Network debugging and diagnostics
