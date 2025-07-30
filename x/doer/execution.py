# ruff: noqa: UP006 UP007 UP043 UP045 UP046
# @omlish-lite
"""
TODO:
 - ** debug mode **
 - ** support for shell ** - write final shell src to tmp file, subprocess shell to that file
 - honor SHELL like however shell=True does
 - PythonParam class lol
 - 'subprocess' helper as used in python code should get the config from DoerTaskConfig.Shell - env and such
"""
import abc
import argparse
import functools
import inspect
import shlex
import subprocess
import sys
import textwrap
import typing as ta

from omlish.funcs.builders import FnBuilder
from omlish.funcs.builders import SimpleFnBuilder
from omlish.lite.cached import cached_nullary
from omlish.lite.check import check
from omlish.lite.json import json_dumps_compact
from omlish.lite.json import json_dumps_pretty
from omlish.lite.marshal import marshal_obj
from omlish.lite.marshal import unmarshal_obj
from omlish.text.minja import MinjaTemplate
from omlish.text.minja import MinjaTemplateParam
from omlish.text.minja import compile_minja_template

from .configs import DoerConfig
from .configs import DoerDefConfig
from .configs import DoerExecutableConfig
from .configs import DoerTaskConfig
from .configs import PythonDoerDefConfig
from .configs import PythonDoerExecutableConfig
from .configs import PythonDoerTaskConfig
from .configs import ShellDoerDefConfig
from .configs import ShellDoerExecutableConfig
from .configs import ShellDoerTaskConfig


DoerExecutableConfigT = ta.TypeVar('DoerExecutableConfigT', bound='DoerExecutableConfig')

ShellDoerExecutableConfigT = ta.TypeVar('ShellDoerExecutableConfigT', bound='ShellDoerExecutableConfig')
PythonDoerExecutableConfigT = ta.TypeVar('PythonDoerExecutableConfigT', bound='PythonDoerExecutableConfig')

DoerTaskConfigT = ta.TypeVar('DoerTaskConfigT', bound='DoerTaskConfig')
DoerDefConfigT = ta.TypeVar('DoerDefConfigT', bound='DoerDefConfig')


##


DoerExecutableConfig  # noqa
PythonDoerExecutableConfig  # noqa
ShellDoerExecutableConfig  # noqa


##


STANDARD_DOER_NS_IMPORTS: ta.Sequence[str] = [
    'codecs',
    'datetime',
    'functools',
    'glob',
    'io',
    'itertools',
    'json',
    'os.path',
    'platform',
    'pprint',
    're',
    'shutil',
    'subprocess',
    'sys',
    'time',
]


@cached_nullary
def standard_doer_ns_imports() -> ta.Mapping[str, ta.Any]:
    return {
        (m := __import__(i)).__name__: m
        for i in STANDARD_DOER_NS_IMPORTS
    }


#


STANDARD_DOER_NS: ta.Mapping[str, ta.Any] = {
    'quote': shlex.quote,

    'python': sys.executable,

    'ta': ta,

    #

    'check': check,

    'json_dumps_compact': json_dumps_compact,
    'json_dumps_pretty': json_dumps_pretty,

    'marshal_obj': marshal_obj,
    'unmarshal_obj': unmarshal_obj,
}


##


class DoerExecutableExecutor(abc.ABC, ta.Generic[DoerExecutableConfigT]):
    def __init__(
            self,
            config: DoerExecutableConfigT,
            *,
            doer_config: DoerConfig = DoerConfig(),
            ns: ta.Optional[ta.Mapping[str, ta.Any]] = None,
            fn_builder: FnBuilder = SimpleFnBuilder(),
    ) -> None:
        super().__init__()

        self._config = config

        self._doer_config = doer_config
        self._init_ns = ns
        self._fn_builder = fn_builder

    @cached_nullary
    def _ns(self) -> ta.Mapping[str, ta.Any]:
        return {
            **standard_doer_ns_imports(),
            **STANDARD_DOER_NS,
            **self._doer_config.consts_ns(),
            **(self._init_ns or {}),
        }

    @abc.abstractmethod
    def execute(self, *args: ta.Any, **kwargs: ta.Any) -> ta.Any:
        raise NotImplementedError


#


class ShellDoerExecutableExecutor(DoerExecutableExecutor[ShellDoerExecutableConfigT], abc.ABC):
    @cached_nullary
    def _template_params(self) -> ta.Sequence[ta.Union[str, MinjaTemplateParam]]:
        return ()

    @cached_nullary
    def _compile_template(self) -> ta.Optional[MinjaTemplate]:
        tmpl_src = self._config.sh
        if tmpl_src and (sh_pa := self._doer_config.shell.joined_preamble()):
            tmpl_src = '\n\n'.join([sh_pa, tmpl_src])
        if tmpl_src is None:
            return None

        return compile_minja_template(
            tmpl_src,
            check.not_isinstance(self._template_params(), str),
            ns=self._ns(),
            strict_strings=True,
            fn_builder=self._fn_builder,
        )


class PythonDoerExecutableExecutor(DoerExecutableExecutor[PythonDoerExecutableConfigT], abc.ABC):
    @cached_nullary
    def _fn_name(self) -> str:
        return '__fn'

    @cached_nullary
    def _params_src(self) -> str:
        return ''

    @cached_nullary
    def _fn_src(self) -> str:
        params_src = self._params_src()
        body_src = self._config.py or 'pass'

        fn_src = '\n'.join([
            f'def {self._fn_name()}({params_src}):',
            textwrap.indent(body_src.strip(), '    '),
        ])

        return fn_src

    @cached_nullary
    def _fn(self) -> ta.Callable[..., ta.Any]:
        return self._fn_builder.build_fn(
            self._fn_name(),
            self._fn_src(),
            self._ns(),
        )


#


class DoerTaskExecutor(DoerExecutableExecutor[DoerTaskConfigT], abc.ABC):
    _ARG_TYPES_BY_TYPE_NAME: ta.Mapping[ta.Optional[str], type] = {
        None: str,
        **{t.__name__: t for t in (int, float, bool)},
    }

    @cached_nullary
    def _args_parser(self) -> ta.Optional[argparse.ArgumentParser]:
        if self._config.args is None:
            return None

        parser = argparse.ArgumentParser()

        for a in self._config.args:
            parser.add_argument(
                *([a.name] if isinstance(a.name, str) else (a.name or [])),
                **(dict(type=self._ARG_TYPES_BY_TYPE_NAME[a.type]) if a.type is not None else {}),  # type: ignore
                **(dict(nargs=a.nargs) if a.nargs else {}),  # type: ignore
                **(dict(default=a.default) if a.default is not None else {}),
            )

        return parser

    @abc.abstractmethod
    def execute(self, *argv: str) -> None:
        raise NotImplementedError


class DoerDefExecutor(DoerExecutableExecutor[DoerDefConfigT], abc.ABC):
    @abc.abstractmethod
    def _do_execute(self, *args: ta.Any, **kwargs: ta.Any) -> ta.Any:
        raise NotImplementedError

    @cached_nullary
    def _do_execute_fn(self) -> ta.Callable[..., ta.Any]:
        fn = self._do_execute

        if self._config.cache:
            max_size: ta.Any = self._config.cache
            if max_size is True:
                max_size = None
            fn = functools.lru_cache(max_size)(fn)

        return fn

    def execute(self, *args: ta.Any, **kwargs: ta.Any) -> ta.Any:
        return self._do_execute_fn()(*args, **kwargs)


#


class ShellDoerTaskExecutor(
    DoerTaskExecutor[ShellDoerTaskConfig],
    ShellDoerExecutableExecutor[ShellDoerTaskConfig],
):
    @cached_nullary
    def _template_params(self) -> ta.Sequence[ta.Union[str, MinjaTemplateParam]]:
        return (
            *super()._template_params(),
            *(['args'] if self._args_parser() is not None else []),
        )

    def execute(self, *argv: str) -> None:
        if (tmpl := self._compile_template()) is None:
            return

        kw: dict = {}
        if (parser := self._args_parser()) is not None:
            kw.update(args=parser.parse_args(argv))
        else:
            check.empty(argv)

        src = tmpl(**kw)

        subprocess.check_call(  # noqa
            src,
            shell=True,
            text=True,
            env=self._doer_config.shell.env,
        )


class PythonDoerTaskExecutor(
    DoerTaskExecutor[PythonDoerTaskConfig],
    PythonDoerExecutableExecutor[PythonDoerTaskConfig],
):
    @cached_nullary
    def _params_src(self) -> str:
        # check.not_(super()._params_src())  # FIXME: PythonParam class
        if self._args_parser() is not None:
            return 'args'
        else:
            return ''

    def execute(self, *argv: str) -> None:
        kw: dict = {}
        if (parser := self._args_parser()) is not None:
            kw.update(args=parser.parse_args(argv))
        else:
            check.empty(argv)

        self._fn()(**kw)


class ShellDoerDefExecutor(
    DoerDefExecutor[ShellDoerDefConfig],
    ShellDoerExecutableExecutor[ShellDoerDefConfig],
):
    @cached_nullary
    def _template_params(self) -> ta.Sequence[ta.Union[str, MinjaTemplateParam]]:
        lst: ta.List[ta.Union[str, MinjaTemplateParam]] = list(super()._template_params())

        ps: ta.List[str]
        if isinstance(self._config.params, str):
            ps = [self._config.params]
        else:
            ps = list(self._config.params or [])

        if ps:
            proto_name = '__proto'
            proto_src = ''.join([
                f'def {proto_name}(',
                *', '.join(ps),
                '): pass',
            ])
            proto_fn = self._fn_builder.build_fn(
                proto_name,
                proto_src,
                self._ns(),
            )
            proto_sig = inspect.signature(proto_fn)
            for pp in proto_sig.parameters.values():
                if pp.default is inspect.Signature.empty:
                    lst.append(MinjaTemplateParam(pp.name))
                else:
                    lst.append(MinjaTemplateParam.new(pp.name, pp.default))

        return lst

    def _do_execute(self, *args: ta.Any, **kwargs: ta.Any) -> str:
        if args:
            raise TypeError(f'{self.__class__.__name__} takes no positional args')

        if (tmpl := self._compile_template()) is None:
            raise NotImplementedError

        src = tmpl(**kwargs)

        out = subprocess.check_output(  # noqa
            src,
            shell=True,
            text=True,
            env=self._doer_config.shell.env,
        )

        if not self._config.preserve_trailing_newlines:
            out = out.rstrip('\n')

        return out


class PythonDoerDefExecutor(
    DoerDefExecutor[PythonDoerDefConfig],
    PythonDoerExecutableExecutor[PythonDoerDefConfig],
):
    @cached_nullary
    def _params_src(self) -> str:
        src = super()._params_src()

        ps: ta.List[str]
        if isinstance(self._config.params, str):
            ps = [self._config.params]
        else:
            ps = list(self._config.params or [])

        if ps:
            src = ', '.join([
                *ps,
                *([src] if src else []),
            ])

        return src

    def _do_execute(self, *args: ta.Any, **kwargs: ta.Any) -> ta.Any:
        return self._fn()(*args, **kwargs)


#


def make_doer_task_executor(
        cfg: DoerTaskConfig,
        **kwargs: ta.Any,
) -> DoerTaskExecutor:
    if isinstance(cfg, ShellDoerTaskConfig):
        return ShellDoerTaskExecutor(cfg, **kwargs)
    elif isinstance(cfg, PythonDoerTaskConfig):
        return PythonDoerTaskExecutor(cfg, **kwargs)
    else:
        raise TypeError(cfg)


def make_doer_def_executor(
        cfg: DoerDefConfig,
        **kwargs: ta.Any,
) -> DoerDefExecutor:
    if isinstance(cfg, ShellDoerDefConfig):
        return ShellDoerDefExecutor(cfg, **kwargs)
    elif isinstance(cfg, PythonDoerDefConfig):
        return PythonDoerDefExecutor(cfg, **kwargs)
    else:
        raise TypeError(cfg)
