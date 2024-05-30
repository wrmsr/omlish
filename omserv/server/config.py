import dataclasses as dc
import typing as ta


BYTES = 1
OCTETS = 1
SECONDS = 1.0


@dc.dataclass(frozen=True)
class Config:
    bind: list[str] = dc.field(default_factory=lambda: ["127.0.0.1:8000"])

    umask: ta.Optional[int] = None
    user: ta.Optional[int] = None
    group: ta.Optional[int] = None

    workers: int = 1

    max_app_queue_size: int = 10

    startup_timeout = 60 * SECONDS
    shutdown_timeout = 60 * SECONDS

    max_requests: ta.Optional[int] = None
    max_requests_jitter: int = 0

    backlog: int = 100

    graceful_timeout: float = 3 * SECONDS

    keep_alive_timeout: float = 5 * SECONDS
    keep_alive_max_requests: int = 1000

    read_timeout: ta.Optional[int] = None

    h11_max_incomplete_size: int = 16 * 1024 * BYTES
    h11_pass_raw_headers: bool = False

    h2_max_concurrent_streams: int = 100
    h2_max_header_list_size: int = 2 ** 16
    h2_max_inbound_frame_size: int = 2 ** 14 * OCTETS

    include_date_header: bool = True
    include_server_header: bool = True
    alt_svc_headers: list[str] = dc.field(default_factory=lambda: [])

    workers: int = 1
