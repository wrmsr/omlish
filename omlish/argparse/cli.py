# ruff: noqa: UP006 UP007
# @omlish-lite
"""
TODO:
 - default command
 - auto match all underscores to hyphens
"""
import argparse
import dataclasses as dc
import functools
import sys
import typing as ta

from ..lite.check import check_arg
from ..lite.check import check_isinstance
from ..lite.check import check_not_empty
from ..lite.check import check_not_in
from ..lite.check import check_not_isinstance


T = ta.TypeVar('T')


##


@dc.dataclass(eq=False)
class ArgparseArg:
    args: ta.Sequence[ta.Any]
    kwargs: ta.Mapping[str, ta.Any]
    dest: ta.Optional[str] = None

    def __get__(self, instance, owner=None):
        if instance is None:
            return self
        return getattr(instance.args, self.dest)  # type: ignore


def argparse_arg(*args, **kwargs) -> ArgparseArg:
    return ArgparseArg(args, kwargs)


#


ArgparseCommandFn = ta.Callable[[], ta.Optional[int]]  # ta.TypeAlias


@dc.dataclass(eq=False)
class ArgparseCommand:
    name: str
    fn: ArgparseCommandFn
    args: ta.Sequence[ArgparseArg] = ()  # noqa

    # _: dc.KW_ONLY

    aliases: ta.Optional[ta.Sequence[str]] = None
    parent: ta.Optional['ArgparseCommand'] = None
    accepts_unknown: bool = False

    def __post_init__(self) -> None:
        def check_name(s: str) -> None:
            check_isinstance(s, str)
            check_not_in('_', s)
            check_not_empty(s)
        check_name(self.name)
        check_not_isinstance(self.aliases, str)
        for a in self.aliases or []:
            check_name(a)

        check_arg(callable(self.fn))
        check_arg(all(isinstance(a, ArgparseArg) for a in self.args))
        check_isinstance(self.parent, (ArgparseCommand, type(None)))
        check_isinstance(self.accepts_unknown, bool)

        functools.update_wrapper(self, self.fn)

    def __get__(self, instance, owner=None):
        if instance is None:
            return self
        return dc.replace(self, fn=self.fn.__get__(instance, owner))  # noqa

    def __call__(self, *args, **kwargs) -> ta.Optional[int]:
        return self.fn(*args, **kwargs)


def argparse_command(
        *args: ArgparseArg,
        name: ta.Optional[str] = None,
        aliases: ta.Optional[ta.Iterable[str]] = None,
        parent: ta.Optional[ArgparseCommand] = None,
        accepts_unknown: bool = False,
) -> ta.Any:  # ta.Callable[[ArgparseCommandFn], ArgparseCommand]:  # FIXME
    for arg in args:
        check_isinstance(arg, ArgparseArg)
    check_isinstance(name, (str, type(None)))
    check_isinstance(parent, (ArgparseCommand, type(None)))
    check_not_isinstance(aliases, str)

    def inner(fn):
        return ArgparseCommand(
            (name if name is not None else fn.__name__).replace('_', '-'),
            fn,
            args,
            aliases=tuple(aliases) if aliases is not None else None,
            parent=parent,
            accepts_unknown=accepts_unknown,
        )

    return inner


##


def _get_argparse_arg_ann_kwargs(ann: ta.Any) -> ta.Mapping[str, ta.Any]:
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


class _ArgparseCliAnnotationBox:
    def __init__(self, annotations: ta.Mapping[str, ta.Any]) -> None:
        super().__init__()
        self.__annotations__ = annotations  # type: ignore


class ArgparseCli:
    def __init__(self, argv: ta.Optional[ta.Sequence[str]] = None) -> None:
        super().__init__()

        self._argv = argv if argv is not None else sys.argv[1:]

        self._args, self._unknown_args = self.get_parser().parse_known_args(self._argv)

    def __init_subclass__(cls, **kwargs: ta.Any) -> None:
        super().__init_subclass__(**kwargs)

        ns = cls.__dict__

        objs = {}
        mro = cls.__mro__[::-1]
        for bns in [bcls.__dict__ for bcls in reversed(mro)] + [ns]:
            bseen = set()  # type: ignore
            for k, v in bns.items():
                if isinstance(v, (ArgparseCommand, ArgparseArg)):
                    check_not_in(v, bseen)
                    bseen.add(v)
                    objs[k] = v
                elif k in objs:
                    del [k]

        anns = ta.get_type_hints(_ArgparseCliAnnotationBox({
            **{k: v for bcls in reversed(mro) for k, v in getattr(bcls, '__annotations__', {}).items()},
            **ns.get('__annotations__', {}),
        }), globalns=ns.get('__globals__', {}))

        if '_parser' in ns:
            parser = check_isinstance(ns['_parser'], argparse.ArgumentParser)
        else:
            parser = argparse.ArgumentParser()
            setattr(cls, '_parser', parser)

        subparsers = parser.add_subparsers()
        for att, obj in objs.items():
            if isinstance(obj, ArgparseCommand):
                if obj.parent is not None:
                    raise NotImplementedError
                for cn in [obj.name, *(obj.aliases or [])]:
                    cparser = subparsers.add_parser(cn)
                    for arg in (obj.args or []):
                        if (
                                len(arg.args) == 1 and
                                isinstance(arg.args[0], str) and
                                not (n := check_isinstance(arg.args[0], str)).startswith('-') and
                                'metavar' not in arg.kwargs
                        ):
                            cparser.add_argument(
                                n.replace('-', '_'),
                                **arg.kwargs,
                                metavar=n,
                            )
                        else:
                            cparser.add_argument(*arg.args, **arg.kwargs)
                    cparser.set_defaults(_cmd=obj)

            elif isinstance(obj, ArgparseArg):
                if att in anns:
                    akwargs = _get_argparse_arg_ann_kwargs(anns[att])
                    obj.kwargs = {**akwargs, **obj.kwargs}
                if not obj.dest:
                    if 'dest' in obj.kwargs:
                        obj.dest = obj.kwargs['dest']
                    else:
                        obj.dest = obj.kwargs['dest'] = att  # type: ignore
                parser.add_argument(*obj.args, **obj.kwargs)

            else:
                raise TypeError(obj)

    _parser: ta.ClassVar[argparse.ArgumentParser]

    @classmethod
    def get_parser(cls) -> argparse.ArgumentParser:
        return cls._parser

    @property
    def argv(self) -> ta.Sequence[str]:
        return self._argv

    @property
    def args(self) -> argparse.Namespace:
        return self._args

    @property
    def unknown_args(self) -> ta.Sequence[str]:
        return self._unknown_args

    def _run_cmd(self, cmd: ArgparseCommand) -> ta.Optional[int]:
        return cmd.__get__(self, type(self))()

    def __call__(self) -> ta.Optional[int]:
        cmd = getattr(self.args, '_cmd', None)

        if self._unknown_args and not (cmd is not None and cmd.accepts_unknown):
            msg = f'unrecognized arguments: {" ".join(self._unknown_args)}'
            if (parser := self.get_parser()).exit_on_error:  # type: ignore
                parser.error(msg)
            else:
                raise argparse.ArgumentError(None, msg)

        if cmd is None:
            self.get_parser().print_help()
            return 0

        return self._run_cmd(cmd)

    def call_and_exit(self) -> ta.NoReturn:
        sys.exit(rc if isinstance(rc := self(), int) else 0)
