main:

- supervisor pidfile
- named instances
- process pidfiles
- log infra
  - rotating
- richer json http endpoints
  - POSTs
- serve http on unix socket
- event listeners
- scheduler
- systemd? less urgent now
- self-update - state handoff - fd's, subprocesses, timers, etc
  - synergy with info http endpoints anyway
- serializable / diffable process cfg, process state

tests:
- more knobs
  - backoff_secs
- more logging (special json event stream)
- in-proc support?
  - `supervisor.step()`
  - injected 'fake' signal manager
- better sync than friggin sleeps
