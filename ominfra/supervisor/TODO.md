main:

- supervisor pidfile
- named instances
- process pidfiles
- log infra (self and forwarded from subprocesses)
  - rotating
- journald no longer default, but supported
- richer json http endpoints
  - POSTs
    - `POST /api/processes/{name}/start` - Start process
    - `POST /api/processes/{name}/stop` - Stop process
    - `POST /api/processes/{name}/signal` - Send signal
    - `GET /api/events?since=N` - Get events (see below)
- serve http on unix socket
- event listeners
  - subprocesses like og supd
  - streaming http endpoints (sse, longpoll)
- scheduler
- systemd? less urgent now
- self-update - state handoff - fd's, subprocesses, timers, etc
  - synergy with info http endpoints anyway
- serializable / diffable process cfg, process state

tests:

- more knobs
  - backoff_secs
- more logging (special json event stream)
  - `{"type": "ProcessStateEvent", "process": "worker", "from": "STARTING", "to": "RUNNING", "ts": 1234.56}`
  - `{"type": "ProcessLogEvent", "process": "worker", "channel": "stdout", "data": "...", "ts": 1234.57}`
- in-proc support?
  - `supervisor.step()`
  - injected 'fake' signal manager
- better sync than friggin sleeps
- more tests:
  - User/UID switching (requires root)
  - Resource limit testing (ulimit)
  - Log file rotation (once implemented)
  - Config reloading (once implemented)
  - num_procs expansion (once fully implemented)
