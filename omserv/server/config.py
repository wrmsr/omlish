import dataclasses as dc
import typing as ta


BYTES = 1
OCTETS = 1
SECONDS = 1.0


@dc.dataclass(frozen=True, kw_only=True)
class Config:
    bind: ta.Sequence[str] = ('127.0.0.1:8000',)

    umask: int | None = None
    user: int | None = None
    group: int | None = None

    workers: int = 0

    max_app_queue_size: int = 10

    startup_timeout = 60 * SECONDS
    shutdown_timeout = 60 * SECONDS

    server_names: ta.Sequence[str] = ()

    max_requests: int | None = None
    max_requests_jitter: int = 0

    backlog: int = 100

    graceful_timeout: float = 3 * SECONDS

    keep_alive_timeout: float = 5 * SECONDS
    keep_alive_max_requests: int = 1000

    read_timeout: int | None = None

    h11_max_incomplete_size: int = 16 * 1024 * BYTES
    h11_pass_raw_headers: bool = False

    h2_max_concurrent_streams: int = 100
    h2_max_header_list_size: int = 2 ** 16
    h2_max_inbound_frame_size: int = 2 ** 14 * OCTETS

    include_date_header: bool = True
    include_server_header: bool = True
    alt_svc_headers: list[str] = dc.field(default_factory=list)

    websocket_max_message_size: int = 16 * 1024 * 1024 * BYTES
    websocket_ping_interval: float | None = None
