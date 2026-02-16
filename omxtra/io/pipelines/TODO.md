### immed

- evented/callback want_read, not a dumb sleep
- meditate on flow control
  - bidirectional?
- meditate on close/eof/errors

### core

- BytesBufferingChannelPipelineHandler or whatever - `def bytes_buffered() -> int`
- re-add BytesChannelPipelineFlowControl unique check (without thrashing cache)?
- 'optional' / 'advisory' event abstract base class? if any non-this isn't 'handled' by some 'driver', raise
    - need to catch stray bytes falling out
- ssl
- drivers
  - 'pure' - no io
  - sync
  - fdio
  - anyio
- scheduler
  - ReadTimeoutHandler
  - idle stuff
  - keepalive
- apps
  - async/await interop
- thread safety? nogil?

### http

- cleanup / standardize / deduplicate / sane-ify buffer configs
  - 'max_chunk_header'? really? it's not the int max it's the max bytes in the buffer..
- make chunk data fields a CanBytes
- ensure parity with urllib/http.server in general
- ensure parity with netty security wise
- request pipelining
- proxy/tunnel connect
- wire into omlish.http.client/server
- Date default server header
- dynamic streaming vs full by app endpoint
- h2 - _will not implement protocol manually_, plug in to `h2` lib

### proto impls

- irc lol
- redis / memcache
- dns?? stub
