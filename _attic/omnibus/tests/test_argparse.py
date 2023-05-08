import argparse
import typing as ta
import weakref

from .. import check
from .. import lang


T = ta.TypeVar('T')
CommandsT = ta.TypeVar('CommandsT')


class Arg:

    def __init__(self, *args, **kwargs) -> None:
        super().__init__()

        self._args = args
        self._kwargs = kwargs

    @property
    def args(self) -> ta.Iterable[ta.Any]:
        return self._args

    @property
    def kwargs(self) -> ta.Mapping[str, ta.Any]:
        return self._kwargs

    def install(self, parser: argparse.ArgumentParser) -> argparse.Action:
        kwargs = dict(self._kwargs)
        group = kwargs.pop('group', None)
        if group is not None:
            check.isinstance(group, str)
            group_parsers = [g for g in parser._action_groups if g.title == group]
            if group_parsers:
                parser = check.single(group_parsers)
            else:
                parser = parser.add_argument_group(group)
        return parser.add_argument(*self.args, **kwargs)

    def get_dest(self) -> str:
        parser = argparse.ArgumentParser(add_help=False)
        self.install(parser)
        action = check.single(parser._actions)
        return action.dest


def arg(*args, **kwargs) -> Arg:
    return Arg(*args, **kwargs)


class Command:

    def __init__(self, fn: ta.Callable, name: str = None) -> None:
        super().__init__()

        self._fn = check.callable(fn)
        self._name = check.not_empty(name if name is not None else fn.__name__.replace('_', '-'))

    @property
    def fn(self) -> ta.Callable:
        return self._fn

    @property
    def name(self) -> str:
        return self._name


_COMMANDS_BY_FN: ta.MutableMapping[ta.Callable, Command] = weakref.WeakKeyDictionary()


def command(*args, **kwargs) -> ta.Callable[[T], T]:
    def inner(fn):
        cmd = Command(fn, *args, **kwargs)
        check.not_in(fn, _COMMANDS_BY_FN)
        _COMMANDS_BY_FN[fn] = cmd
        return fn
    return inner


class Commands(lang.Abstract):

    @classmethod
    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)


def get_commands(obj: ta.Union[ta.Type[CommandsT], Commands]) -> ta.Dict[str, Command]:
    if isinstance(obj, Commands):
        cls = type(obj)
    elif isinstance(obj, type) and issubclass(obj, Commands):
        cls = obj
    else:
        raise TypeError(obj)

    ret = {}
    for bcls in reversed(cls.__mro__):
        for k, v in bcls.__dict__.items():
            try:
                cmd = _COMMANDS_BY_FN[v]
            except (KeyError, TypeError):
                pass
            else:
                ret[cmd.name] = cmd

    return ret


class TestCommands(Commands):

    @command()
    def frob(self):
        pass


def test_argparse():
    cmds = TestCommands()
    cmds.frob()
    print(get_commands(cmds))
