# ruff: noqa: UP006 UP007
import dataclasses as dc
import os
import typing as ta


T = ta.TypeVar('T')


##


@dc.dataclass(frozen=True)
class ShellCmd:
    s: str

    env: ta.Optional[ta.Mapping[str, str]] = None

    def build_run_kwargs(
            self,
            *,
            env: ta.Optional[ta.Mapping[str, str]] = None,
            **kwargs: ta.Any,
    ) -> ta.Dict[str, ta.Any]:
        if env is None:
            env = os.environ
        if self.env:
            if (ek := set(env) & set(self.env)):
                raise KeyError(*ek)
            env = {**env, **self.env}

        return dict(
            env=env,
            **kwargs,
        )

    def run(self, fn: ta.Callable[..., T], **kwargs) -> T:
        return fn(
            'sh', '-c', self.s,
            **self.build_run_kwargs(**kwargs),
        )
