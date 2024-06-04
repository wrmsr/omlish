"""
TODO:
 - default command
"""
import argparse
import dataclasses as dc
import functools
import sys
import typing as ta

from . import c3
from . import check


T = ta.TypeVar('T')


SUPPRESS = argparse.SUPPRESS

OPTIONAL = argparse.OPTIONAL
ZERO_OR_MORE = argparse.ZERO_OR_MORE
ONE_OR_MORE = argparse.ONE_OR_MORE
PARSER = argparse.PARSER
REMAINDER = argparse.REMAINDER

HelpFormatter = argparse.HelpFormatter
RawDescriptionHelpFormatter = argparse.RawDescriptionHelpFormatter
RawTextHelpFormatter = argparse.RawTextHelpFormatter
ArgumentDefaultsHelpFormatter = argparse.ArgumentDefaultsHelpFormatter

MetavarTypeHelpFormatter = argparse.MetavarTypeHelpFormatter

ArgumentError = argparse.ArgumentError
ArgumentTypeError = argparse.ArgumentTypeError

Action = argparse.Action
BooleanOptionalAction = argparse.BooleanOptionalAction
SubParsersAction = argparse._SubParsersAction  # noqa

FileType = argparse.FileType

Namespace = argparse.Namespace

ArgumentParser = argparse.ArgumentParser


@dc.dataclass(eq=False)
class Arg:
    args: ta.Sequence[ta.Any]
    kwargs: ta.Mapping[str, ta.Any]
    dest: ta.Optional[str] = None

    def __get__(self, instance, owner=None):
        if instance is None:
            return self
        return getattr(instance.args, self.dest)  # type: ignore


def arg(*args, **kwargs) -> Arg:
    return Arg(args, kwargs)


CommandFn = ta.Callable[[], None]


@dc.dataclass(eq=False)
class Command:
    name: str
    fn: CommandFn
    args: ta.Sequence[Arg] = ()
    parent: ta.Optional['Command'] = None

    def __post_init__(self) -> None:
        check.isinstance(self.name, str)
        check.not_in('-', self.name)
        check.not_empty(self.name)

        check.callable(self.fn)
        check.arg(all(isinstance(a, Arg) for a in self.args))
        check.isinstance(self.parent, (Command, None))

        functools.update_wrapper(self, self.fn)

    def __get__(self, instance, owner=None):
        if instance is None:
            return self
        return dc.replace(self, fn=self.fn.__get__(instance, owner))

    def __call__(self, *args, **kwargs) -> None:
        return self.fn(*args, **kwargs)


def command(
        *args: Arg,
        name: ta.Optional[str] = None,
        parent: ta.Optional[Command] = None,
) -> ta.Any:  # ta.Callable[[CommandFn], Command]:  # FIXME
    for arg in args:
        check.isinstance(arg, Arg)
    check.isinstance(name, (str, None))
    check.isinstance(parent, (Command, None))

    def inner(fn):
        return Command(
            (name if name is not None else fn.__name__).replace('-', '_'),
            fn,
            args,
            parent=parent,
        )

    return inner


def get_arg_ann_kwargs(ann: ta.Any) -> ta.Mapping[str, ta.Any]:
    if ann is str:
        return {}
    elif ann is int:
        return {'type': int}
    elif ann is bool:
        return {'action': 'store_true'}
    elif ann is list:
        return {'action': 'append'}
    else:
        raise TypeError(ann)


class _AnnotationBox:

    def __init__(self, annotations: ta.Mapping[str, ta.Any]) -> None:
        super().__init__()
        self.__annotations__ = annotations  # type: ignore


class _CliMeta(type):

    def __new__(mcls, name: str, bases: ta.Sequence[type], namespace: ta.Mapping[str, ta.Any]) -> type:
        if not bases:
            return super().__new__(mcls, name, tuple(bases), dict(namespace))

        bases = list(bases)
        namespace = dict(namespace)

        objs = {}
        mro = c3.merge([list(b.__mro__) for b in bases])
        for bns in [bcls.__dict__ for bcls in reversed(mro)] + [namespace]:
            bseen = set()  # type: ignore
            for k, v in bns.items():
                if isinstance(v, (Command, Arg)):
                    check.not_in(v, bseen)
                    bseen.add(v)
                    objs[k] = v
                elif k in objs:
                    del [k]

        anns = ta.get_type_hints(_AnnotationBox({
            **{k: v for bcls in reversed(mro) for k, v in getattr(bcls, '__annotations__', {}).items()},
            **namespace.get('__annotations__', {}),
        }), globalns=namespace.get('__globals__', {}))

        if 'parser' in namespace:
            parser = check.isinstance(namespace.pop('parser'), ArgumentParser)
        else:
            parser = ArgumentParser()
        namespace['_parser'] = parser

        subparsers = parser.add_subparsers()
        for name, obj in objs.items():
            if isinstance(obj, Command):
                if obj.parent is not None:
                    raise NotImplementedError
                cparser = subparsers.add_parser(obj.name)
                for arg in (obj.args or []):
                    cparser.add_argument(*arg.args, **arg.kwargs)
                cparser.set_defaults(_cmd=obj)

            elif isinstance(obj, Arg):
                if name in anns:
                    akwargs = get_arg_ann_kwargs(anns[name])
                    obj.kwargs = {**akwargs, **obj.kwargs}
                if not obj.dest:
                    if 'dest' in obj.kwargs:
                        obj.dest = obj.kwargs['dest']
                    else:
                        obj.dest = obj.kwargs['dest'] = name  # type: ignore
                parser.add_argument(*obj.args, **obj.kwargs)

            else:
                raise TypeError(obj)

        return super().__new__(mcls, name, tuple(bases), namespace)


class Cli(metaclass=_CliMeta):

    def __init__(self, argv: ta.Optional[ta.Sequence[str]] = None) -> None:
        super().__init__()

        self._argv = argv if argv is not None else sys.argv[1:]
        self._args = self.get_parser().parse_args(self._argv)

    _parser: ta.ClassVar[ArgumentParser]

    @classmethod
    def get_parser(cls) -> ArgumentParser:
        return cls._parser

    @property
    def argv(self) -> ta.Sequence[str]:
        return self._argv

    @property
    def args(self) -> Namespace:
        return self._args

    def _run_cmd(self, cmd: Command) -> None:
        cmd.__get__(self, type(self))()

    def __call__(self) -> None:
        cmd = getattr(self.args, '_cmd', None)
        if cmd is None:
            self.get_parser().print_help()
            return
        self._run_cmd(cmd)
