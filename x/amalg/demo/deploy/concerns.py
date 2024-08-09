import abc
import dataclasses as dc
import enum
import typing as ta


class Phase(enum.Enum):
    HOST = enum.auto()
    ENV = enum.auto()
    BACKEND = enum.auto()
    FRONTEND = enum.auto()
    START_BACKEND = enum.auto()
    START_FRONTEND = enum.auto()


def run_in_phase(*ps: Phase):
    def inner(fn):
        fn.__deployment_phases__ = ps
        return fn
    return inner


class Concern(abc.ABC):
    def __init__(self, d: 'Deployment') -> None:
        super().__init__()
        self._d = d

    _phase_fns: ta.ClassVar[ta.Mapping[Phase, ta.Sequence[ta.Callable]]]

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        dct: ta.Dict[Phase, ta.List[ta.Callable]] = {}
        for fn, ps in [
            (v, ps)
            for a in dir(cls)
            if not (a.startswith('__') and a.endswith('__'))
            for v in [getattr(cls, a, None)]
            for ps in [getattr(v, '__deployment_phases__', None)]
            if ps
        ]:
            dct.update({p: [*dct.get(p, []), fn] for p in ps})
        cls._phase_fns = dct

    @dc.dataclass(frozen=True)
    class Output(abc.ABC):
        path: str
        is_file: bool

    def outputs(self) -> ta.Sequence[Output]:
        return ()

    def run_phase(self, p: Phase) -> None:
        for fn in self._phase_fns.get(p, ()):
            fn.__get__(self, type(self))()
