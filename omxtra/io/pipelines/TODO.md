### immed

- shutdown sequence / error handling
  - more channel states lol
  - send FinalInput in destroy if it hasn't been?
    - is destroy fully 'runnable'? no, it can't feed_out
- reimpl full (bytes) flow control (watermarks)
  - bidirectional?
- hand optimize a bit
  - segmented split_to should mutate seg list in place

### core

- revive DESIGN.md
- ssl
  - `ssl.MemoryBIO -> ctx.wrap_bio -> while True: sslobj.do_handshake() -> except ssl.SSLWantReadError, ssl.SSLWantWriteError, ...`
- drivers
  - 'pure' - no io
  - sync
  - fdio
  - anyio
- scheduler goodies
  - ReadTimeoutHandler
  - idle stuff
  - keepalive
- thread safety? nogil?
- inject interop
- interleavable inter-stage message queueing handler? usecases?
- removed callbacks
  - do netty ByteToMessageDecoder removal handling
  - also removing in flight might mess stuff up (STARTTLS?)

### http

- ensure parity with urllib/http.server in general
- ensure parity with netty security wise
- request pipelining
- proxy/tunnel connect
- wire into omlish.http.client/server
- Date default server header
- dynamic streaming vs full by app endpoint
- h2 - _will not implement protocol manually_, plug in to `h2` lib
- lean on ParsedHeaders more - validly-duplicate-but-identical content-length currently isn't handled for ex.
- dangerous switch to not validate http headers

### proto impls

- websocket
- irc lol
- dns?? stub
- proto / grpc
- redis / memcache
- db drivers?
