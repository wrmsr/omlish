# ruff: noqa: UP006 UP007
import signal
import typing as ta


##


_SIG_NAMES: ta.Optional[ta.Mapping[int, str]] = None


def sig_name(sig: int) -> str:
    global _SIG_NAMES
    if _SIG_NAMES is None:
        _SIG_NAMES = _init_sig_names()
    return _SIG_NAMES.get(sig) or 'signal %d' % sig


def _init_sig_names() -> ta.Dict[int, str]:
    d = {}
    for k, v in signal.__dict__.items():  # noqa
        k_startswith = getattr(k, 'startswith', None)
        if k_startswith is None:
            continue
        if k_startswith('SIG') and not k_startswith('SIG_'):
            d[v] = k
    return d


##


class SignalReceiver:
    def __init__(self) -> None:
        super().__init__()

        self._signals_recvd: ta.List[int] = []

    def receive(self, sig: int, frame: ta.Any) -> None:
        if sig not in self._signals_recvd:
            self._signals_recvd.append(sig)

    def install(self, *sigs: int) -> None:
        for sig in sigs:
            signal.signal(sig, self.receive)

    def get_signal(self) -> ta.Optional[int]:
        if self._signals_recvd:
            sig = self._signals_recvd.pop(0)
        else:
            sig = None
        return sig
