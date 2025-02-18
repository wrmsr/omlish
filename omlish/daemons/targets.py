import abc
import functools
import os
import typing as ta

from .. import check
from .. import dataclasses as dc
from .. import lang


if ta.TYPE_CHECKING:
    import runpy
else:
    runpy = lang.proxy_import('runpy')


##


class Target(dc.Case):
    @classmethod
    def of(cls, obj: ta.Any) -> 'Target':
        if isinstance(obj, Target):
            return obj

        elif isinstance(obj, str):
            return NameTarget(obj)

        elif callable(obj):
            return FnTarget(obj)

        else:
            raise TypeError(obj)


class TargetRunner(abc.ABC):
    @abc.abstractmethod
    def run(self) -> None:
        raise NotImplementedError


@functools.singledispatch
def target_runner_for(target: Target) -> TargetRunner:
    raise TypeError(target)


##


class FnTarget(Target):
    fn: ta.Callable[[], None]


class FnTargetRunner(TargetRunner, dc.Frozen):
    target: FnTarget

    def run(self) -> None:
        self.target.fn()


@target_runner_for.register
def _(target: FnTarget) -> FnTargetRunner:
    return FnTargetRunner(target)


##


class NameTarget(Target):
    name: str

    @classmethod
    def for_obj(
            cls,
            obj: ta.Any,
            *,
            globals: ta.Mapping[str, ta.Any] | None = None,  # noqa
            no_module_name_lookup: bool = False,
    ) -> 'NameTarget':
        if globals is None:
            globals = obj.__globals__  # noqa
        if not no_module_name_lookup:
            mn = lang.get_real_module_name(globals)
        else:
            mn = globals['__name__']
        qn = obj.__qualname__
        return NameTarget('.'.join([mn, qn]))


class NameTargetRunner(TargetRunner, dc.Frozen):
    target: NameTarget

    def run(self) -> None:
        name = self.target.name
        if lang.can_import(name):
            runpy._run_module_as_main(name)  # type: ignore  # noqa
        else:
            obj = lang.import_attr(self.target.name)
            tgt = Target.of(obj)
            tr = target_runner_for(tgt)
            return tr.run()


@target_runner_for.register
def _(target: NameTarget) -> NameTargetRunner:
    return NameTargetRunner(target)


##


class ExecTarget(Target):
    cmd: ta.Sequence[str] = dc.xfield(coerce=check.of_not_isinstance(str))


class ExecTargetRunner(TargetRunner, dc.Frozen):
    target: ExecTarget

    def run(self) -> None:
        os.execl(*self.target.cmd)


@target_runner_for.register
def _(target: ExecTarget) -> ExecTargetRunner:
    return ExecTargetRunner(target)
