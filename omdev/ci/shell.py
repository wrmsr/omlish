# ruff: noqa: UP006 UP007
# @omlish-lite
import dataclasses as dc
import typing as ta


T = ta.TypeVar('T')


##


@dc.dataclass(frozen=True)
class ShellCmd:
    s: str

    @property
    def run_kwargs(self) -> ta.Dict[str, ta.Any]:
        return {}

    def run(self, fn: ta.Callable[..., T], **kwargs) -> T:
        return fn(
            'sh', '-c', self.s,
            **self.run_kwargs,
            **kwargs,
        )
