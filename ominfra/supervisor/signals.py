# ruff: noqa: UP006 UP007
import signal
import typing as ta


##


_SIGS_BY_NUM: ta.Mapping[int, signal.Signals] = {s.value: s for s in signal.Signals}
_SIGS_BY_NAME: ta.Mapping[str, signal.Signals] = {s.name: s for s in signal.Signals}


def sig_num(value: ta.Union[int, str]) -> int:
    try:
        num = int(value)

    except (ValueError, TypeError):
        name = value.strip().upper()  # type: ignore
        if not name.startswith('SIG'):
            name = f'SIG{name}'

        if (sn := _SIGS_BY_NAME.get(name)) is None:
            raise ValueError(f'value {value!r} is not a valid signal name')  # noqa
        num = sn

    if num not in _SIGS_BY_NUM:
        raise ValueError(f'value {value!r} is not a valid signal number')

    return num


def sig_name(num: int) -> str:
    if (sig := _SIGS_BY_NUM.get(num)) is not None:
        return sig.name
    return f'signal {sig}'


##


class SignalReceiver:
    def __init__(self) -> None:
        super().__init__()

        self._signals_recvd: ta.List[int] = []

    def receive(self, sig: int, frame: ta.Any = None) -> None:
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
