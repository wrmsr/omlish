SocketAddress: ta.TypeAlias = ta.Any


##


@dc.dataclass(frozen=True)
class AddrInfoArgs:
    host: str | None
    port: str | int | None
    family: socket.AddressFamily = socket.AddressFamily.AF_UNSPEC
    type: int = 0
    proto: int = 0
    flags: socket.AddressInfo = socket.AddressInfo(0)


@dc.dataclass(frozen=True)
class AddrInfo:
    family: socket.AddressFamily
    type: int
    proto: int
    canonname: str | None
    sockaddr: SocketAddress


def get_best_family(*address) -> tuple[socket.AddressFamily, SocketAddress]:
    infos = socket.getaddrinfo(
        *address,
        type=socket.SOCK_STREAM,
        flags=socket.AI_PASSIVE,
    )
    ai = AddrInfo(*next(iter(infos)))
    return ai.family, ai.sockaddr


##


class StreamRequestHandler(abc.ABC):
    def __init__(
            self,
            client_address: SocketAddress,
            rfile: ta.IO,
            wfile: ta.IO,
    ) -> None:
        super().__init__()

        self.client_address = client_address
        self.rfile = rfile
        self.wfile = wfile

    @abc.abstractmethod
    def handle(self) -> None:
        raise NotImplementedError
