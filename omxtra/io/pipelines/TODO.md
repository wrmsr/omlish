### immed

- meditate on close/eof/errors
- evented/callback want_read, not a dumb sleep
- meditate on flow control
  - bidirectional?
- need to catch stray bytes falling out
  - 'Ignorable' event abstract base class? if any non-this isn't 'handled' by some 'driver', raise

### core

- revive DESIGN.md
- BytesBufferingChannelPipelineHandler or whatever - `def bytes_buffered() -> int`
- re-add BytesChannelPipelineFlowControl unique check (without thrashing cache)?
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
- inject interop
- interleavable inter-stage message queueing handler? usecases?
- dont catch BaseException lol - or at least have exception reraise filter (ex. cancelled)
- removed callbacks
  - currently just blow up everything if they raise lol
  - also removing in flight might mess stuff up (STARTTLS?)

### http

- cleanup / standardize / deduplicate / sane-ify buffer configs
  - 'max_chunk_header'? really? it's not the int max it's the max bytes in the buffer..
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

- irc lol
- redis / memcache
- dns?? stub
