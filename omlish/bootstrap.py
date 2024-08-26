"""
TODO:
 - more logging options
 - a more powerful interface would be run_fn_with_bootstrap..

TODO new items:
 - pydevd connect-back
 - debugging / pdb
 - repl server
 - packaging fixups
 - daemonize ( https://github.com/thesharp/daemonize/blob/master/daemonize.py )
"""
# ruff: noqa: UP006 UP007
import abc
import argparse
import contextlib
import dataclasses as dc
import enum
import faulthandler
import gc
import importlib
import io
import itertools
import logging
import os
import pwd
import resource
import signal
import sys
import typing as ta

from . import lang


if ta.TYPE_CHECKING:
    import cProfile  # noqa
    import pstats
    import runpy

    from . import libc
    from . import logs
    from . import os as osu
    from .diag import threads as diagt
    from .formats import dotenv

else:
    cProfile = lang.proxy_import('cProfile')  # noqa
    pstats = lang.proxy_import('pstats')
    runpy = lang.proxy_import('runpy')

    libc = lang.proxy_import('.libc', __package__)
    logs = lang.proxy_import('.logs', __package__)
    osu = lang.proxy_import('.os', __package__)
    diagt = lang.proxy_import('.diag.threads', __package__)
    dotenv = lang.proxy_import('.formats.dotenv', __package__)


BootstrapConfigT = ta.TypeVar('BootstrapConfigT', bound='Bootstrap.Config')


##


class Bootstrap(abc.ABC, ta.Generic[BootstrapConfigT]):
    @dc.dataclass(frozen=True)
    class Config(abc.ABC):  # noqa
        pass

    def __init__(self, config: BootstrapConfigT) -> None:
        super().__init__()
        self._config = config

    def __init_subclass__(cls, **kwargs: ta.Any) -> None:
        super().__init_subclass__(**kwargs)
        if not cls.__name__.endswith('Bootstrap'):
            raise NameError(cls)
        if abc.ABC not in cls.__bases__ and not issubclass(cls.__dict__['Config'], Bootstrap.Config):
            raise TypeError(cls)


class SimpleBootstrap(Bootstrap[BootstrapConfigT], abc.ABC):
    @abc.abstractmethod
    def run(self) -> None:
        raise NotImplementedError


class ContextBootstrap(Bootstrap[BootstrapConfigT], abc.ABC):
    @abc.abstractmethod
    def enter(self) -> ta.ContextManager[None]:
        raise NotImplementedError


##


class CwdBootstrap(ContextBootstrap['CwdBootstrap.Config']):
    @dc.dataclass(frozen=True)
    class Config(Bootstrap.Config):
        path: ta.Optional[str] = None

    @contextlib.contextmanager
    def enter(self) -> ta.Iterator[None]:
        if self._config.path is not None:
            prev = os.getcwd()
            os.chdir(self._config.path)
        else:
            prev = None

        try:
            yield

        finally:
            if prev is not None:
                os.chdir(prev)


##


class SetuidBootstrap(SimpleBootstrap['SetuidBootstrap.Config']):
    @dc.dataclass(frozen=True)
    class Config(Bootstrap.Config):
        user: ta.Optional[str] = None

    def run(self) -> None:
        if self._config.user is not None:
            user = pwd.getpwnam(self._config.user)
            os.setuid(user.pw_uid)


##


class GcDebugFlag(enum.Enum):
    STATS = gc.DEBUG_STATS
    COLLECTABLE = gc.DEBUG_COLLECTABLE
    UNCOLLECTABLE = gc.DEBUG_UNCOLLECTABLE
    SAVEALL = gc.DEBUG_SAVEALL
    LEAK = gc.DEBUG_LEAK


class GcBootstrap(ContextBootstrap['GcBootstrap.Config']):
    @dc.dataclass(frozen=True)
    class Config(Bootstrap.Config):
        disable: bool = False
        debug: ta.Optional[int] = None

    @contextlib.contextmanager
    def enter(self) -> ta.Iterator[None]:
        prev_enabled = gc.isenabled()
        if self._config.disable:
            gc.disable()

        if self._config.debug is not None:
            prev_debug = gc.get_debug()
            gc.set_debug(self._config.debug)
        else:
            prev_debug = None

        try:
            yield

        finally:
            if prev_enabled:
                gc.enable()

            if prev_debug is not None:
                gc.set_debug(prev_debug)


##


class NiceBootstrap(SimpleBootstrap['NiceBootstrap.Config']):
    @dc.dataclass(frozen=True)
    class Config(Bootstrap.Config):
        nice: ta.Optional[int] = None

    def run(self) -> None:
        if self._config.nice is not None:
            os.nice(self._config.nice)


##


class LogBootstrap(ContextBootstrap['LogBootstrap.Config']):
    @dc.dataclass(frozen=True)
    class Config(Bootstrap.Config):
        level: ta.Union[str, int, None] = None
        json: bool = False

    @contextlib.contextmanager
    def enter(self) -> ta.Iterator[None]:
        if self._config.level is None:
            yield
            return

        handler = logs.configure_standard_logging(
            self._config.level,
            json=self._config.json,
        )

        try:
            yield

        finally:
            if handler is not None:
                logging.root.removeHandler(handler)


##


class FaulthandlerBootstrap(ContextBootstrap['FaulthandlerBootstrap.Config']):
    @dc.dataclass(frozen=True)
    class Config(Bootstrap.Config):
        enabled: ta.Optional[bool] = None

    @contextlib.contextmanager
    def enter(self) -> ta.Iterator[None]:
        if self._config.enabled is None:
            yield
            return

        prev = faulthandler.is_enabled()
        if self._config.enabled:
            faulthandler.enable()
        else:
            faulthandler.disable()

        try:
            yield

        finally:
            if prev:
                faulthandler.enable()
            else:
                faulthandler.disable()


##


SIGNALS_BY_NAME = {
    a[len('SIG'):]: v  # noqa
    for a in dir(signal)
    if a.startswith('SIG')
    and not a.startswith('SIG_')
    and a == a.upper()
    and isinstance((v := getattr(signal, a)), int)
}


class PrctlBootstrap(SimpleBootstrap['PrctlBootstrap.Config']):
    @dc.dataclass(frozen=True)
    class Config(Bootstrap.Config):
        dumpable: bool = False
        deathsig: ta.Union[int, str, None] = None

    def run(self) -> None:
        if self._config.dumpable:
            libc.prctl(libc.PR_SET_DUMPABLE, 1, 0, 0, 0, 0)

        if self._config.deathsig is not None:
            if isinstance(self._config.deathsig, int):
                sig = self._config.deathsig
            else:
                sig = SIGNALS_BY_NAME[self._config.deathsig.upper()]
            libc.prctl(libc.PR_SET_PDEATHSIG, sig, 0, 0, 0, 0)


##


RLIMITS_BY_NAME = {
    a[len('RLIMIT_'):]: v  # noqa
    for a in dir(resource)
    if a.startswith('RLIMIT_')
    and a == a.upper()
    and isinstance((v := getattr(resource, a)), int)
}


class RlimitBootstrap(ContextBootstrap['RlimitBootstrap.Config']):
    @dc.dataclass(frozen=True)
    class Config(Bootstrap.Config):
        limits: ta.Optional[ta.Mapping[str, ta.Tuple[ta.Optional[int], ta.Optional[int]]]] = None

    @contextlib.contextmanager
    def enter(self) -> ta.Iterator[None]:
        if not self._config.limits:
            yield
            return

        def or_infin(l: ta.Optional[int]) -> int:
            return l if l is not None else resource.RLIM_INFINITY

        prev = {}
        for k, (s, h) in self._config.limits.items():
            i = RLIMITS_BY_NAME[k.upper()]
            prev[i] = resource.getrlimit(i)
            resource.setrlimit(i, (or_infin(s), or_infin(h)))

        try:
            yield

        finally:
            for i, (s, h) in prev.items():
                resource.setrlimit(i, (s, h))


##


class ImportBootstrap(SimpleBootstrap['ImportBootstrap.Config']):
    @dc.dataclass(frozen=True)
    class Config(Bootstrap.Config):
        modules: ta.Optional[ta.Sequence[str]] = None

    def run(self) -> None:
        for m in self._config.modules or ():
            importlib.import_module(m)


##


class ProfilingBootstrap(ContextBootstrap['ProfilingBootstrap.Config']):
    @dc.dataclass(frozen=True)
    class Config(Bootstrap.Config):
        enable: bool = False
        builtins: bool = True

        outfile: ta.Optional[str] = None

        print: bool = False
        sort: str = 'cumtime'
        topn: int = 100

    @contextlib.contextmanager
    def enter(self) -> ta.Iterator[None]:
        if not self._config.enable:
            yield
            return

        prof = cProfile.Profile()
        prof.enable()
        try:
            yield

        finally:
            prof.disable()
            prof.create_stats()

            if self._config.print:
                pstats.Stats(prof) \
                    .strip_dirs() \
                    .sort_stats(self._config.sort) \
                    .print_stats(self._config.topn)

            if self._config.outfile is not None:
                prof.dump_stats(self._config.outfile)


##


class EnvBootstrap(ContextBootstrap['EnvBootstrap.Config']):
    @dc.dataclass(frozen=True)
    class Config(Bootstrap.Config):
        vars: ta.Optional[ta.Mapping[str, ta.Optional[str]]] = None
        files: ta.Optional[ta.Sequence[str]] = None

    @contextlib.contextmanager
    def enter(self) -> ta.Iterator[None]:
        if not (self._config.vars or self._config.files):
            yield
            return

        new = dict(self._config.vars or {})
        for f in self._config.files or ():
            new.update(dotenv.dotenv_values(f, env=os.environ))

        prev: ta.Dict[str, ta.Optional[str]] = {k: os.environ.get(k) for k in new}

        def do(k: str, v: ta.Optional[str]) -> None:
            if v is not None:
                os.environ[k] = v
            else:
                del os.environ[k]

        for k, v in new.items():
            do(k, v)

        try:
            yield

        finally:
            for k, v in prev.items():
                do(k, v)


##


class ThreadDumpBootstrap(ContextBootstrap['ThreadDumpBootstrap.Config']):
    @dc.dataclass(frozen=True)
    class Config(Bootstrap.Config):
        interval_s: ta.Optional[float] = None

        on_sigquit: bool = False

    @contextlib.contextmanager
    def enter(self) -> ta.Iterator[None]:
        if self._config.interval_s:
            tdt = diagt.create_thread_dump_thread(
                interval_s=self._config.interval_s,
                start=True,
            )
        else:
            tdt = None

        if self._config.on_sigquit:
            dump_threads_str = diagt.dump_threads_str

            def handler(signum, frame):
                print(dump_threads_str(), file=sys.stderr)

            prev_sq = lang.just(signal.signal(signal.SIGQUIT, handler))
        else:
            prev_sq = lang.empty()

        try:
            yield

        finally:
            if tdt is not None:
                tdt.stop_nowait()

            if prev_sq.present:
                signal.signal(signal.SIGQUIT, prev_sq.must())


##


class TimebombBootstrap(ContextBootstrap['TimebombBootstrap.Config']):
    @dc.dataclass(frozen=True)
    class Config(Bootstrap.Config):
        delay_s: ta.Optional[float] = None

    @contextlib.contextmanager
    def enter(self) -> ta.Iterator[None]:
        if not self._config.delay_s:
            yield
            return

        tbt = diagt.create_timebomb_thread(
            self._config.delay_s,
            start=True,
        )
        try:
            yield
        finally:
            tbt.stop_nowait()


##


class PidfileBootstrap(ContextBootstrap['PidfileBootstrap.Config']):
    @dc.dataclass(frozen=True)
    class Config(Bootstrap.Config):
        path: ta.Optional[str] = None

    @contextlib.contextmanager
    def enter(self) -> ta.Iterator[None]:
        if self._config.path is None:
            yield
            return

        with osu.Pidfile(self._config.path) as pf:
            pf.write()
            yield


##


class FdsBootstrap(SimpleBootstrap['FdsBootstrap.Config']):
    @dc.dataclass(frozen=True)
    class Config(Bootstrap.Config):
        redirects: ta.Optional[ta.Mapping[int, ta.Union[int, str, None]]] = None

    def run(self) -> None:
        for dst, src in (self._config.redirects or {}).items():
            if src is None:
                src = '/dev/null'
            if isinstance(src, int):
                os.dup2(src, dst)
            elif isinstance(src, str):
                sfd = os.open(src, os.O_RDWR)
                os.dup2(sfd, dst)
                os.close(sfd)
            else:
                raise TypeError(src)


##


class PrintPidBootstrap(SimpleBootstrap['PrintPidBootstrap.Config']):
    @dc.dataclass(frozen=True)
    class Config(Bootstrap.Config):
        enable: bool = False
        pause: bool = False

    def run(self) -> None:
        if not (self._config.enable or self._config.pause):
            return
        print(str(os.getpid()), file=sys.stderr)
        if self._config.pause:
            input()


##


BOOTSTRAP_TYPES_BY_NAME: ta.Mapping[str, ta.Type[Bootstrap]] = {  # noqa
    lang.snake_case(cls.__name__[:-len('Bootstrap')]): cls
    for cls in lang.deep_subclasses(Bootstrap)
    if not lang.is_abstract_class(cls)
}

BOOTSTRAP_TYPES_BY_CONFIG_TYPE: ta.Mapping[ta.Type[Bootstrap.Config], ta.Type[Bootstrap]] = {
    cls.Config: cls
    for cls in BOOTSTRAP_TYPES_BY_NAME.values()
}


##


class BootstrapHarness:
    def __init__(self, lst: ta.Sequence[Bootstrap]) -> None:
        super().__init__()
        self._lst = lst

    @contextlib.contextmanager
    def __call__(self) -> ta.Iterator[None]:
        with contextlib.ExitStack() as es:
            for c in self._lst:
                if isinstance(c, SimpleBootstrap):
                    c.run()
                elif isinstance(c, ContextBootstrap):
                    es.enter_context(c.enter())
                else:
                    raise TypeError(c)

            yield


##


@contextlib.contextmanager
def bootstrap(*cfgs: Bootstrap.Config) -> ta.Iterator[None]:
    with BootstrapHarness([
        BOOTSTRAP_TYPES_BY_CONFIG_TYPE[type(c)](c)
        for c in cfgs
    ])():
        yield


##


class _OrderedArgsAction(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        if 'ordered_args' not in namespace:
            setattr(namespace, 'ordered_args', [])
        if self.const is not None:
            value = self.const
        else:
            value = values
        namespace.ordered_args.append((self.dest, value))


def _or_opt(ty):
    return (ty, ta.Optional[ty])


def _int_or_str(v):
    try:
        return int(v)
    except ValueError:
        return v


def _add_arguments(parser: argparse.ArgumentParser) -> None:
    # ta.Optional[ta.Mapping[str, ta.Tuple[ta.Optional[int], ta.Optional[int]]]]

    for cname, cls in BOOTSTRAP_TYPES_BY_NAME.items():
        for fld in dc.fields(cls.Config):
            aname = f'--{cname}:{fld.name}'
            kw: ta.Dict[str, ta.Any] = {}

            if fld.type in _or_opt(str):
                pass
            elif fld.type in _or_opt(bool):
                kw.update(const=True, nargs=0)
            elif fld.type in _or_opt(int):
                kw.update(type=int)
            elif fld.type in _or_opt(float):
                kw.update(type=float)
            elif fld.type in _or_opt(ta.Union[int, str]):
                kw.update(type=_int_or_str)

            elif fld.type in (
                    *_or_opt(ta.Sequence[str]),
                    *_or_opt(ta.Mapping[str, ta.Optional[str]]),
                    *_or_opt(ta.Mapping[int, ta.Union[int, str, None]]),
                    *_or_opt(ta.Mapping[str, ta.Tuple[ta.Optional[int], ta.Optional[int]]]),
            ):
                if aname[-1] != 's':
                    raise NameError(aname)
                aname = aname[:-1]

            else:
                raise TypeError(fld)

            parser.add_argument(aname, action=_OrderedArgsAction, **kw)


def _process_arguments(args: ta.Any) -> ta.Sequence[Bootstrap.Config]:
    if not (oa := getattr(args, 'ordered_args', None)):
        return []

    cfgs: ta.List[Bootstrap.Config] = []

    for cname, cargs in [
        (n, list(g))
        for n, g in
        itertools.groupby(oa, key=lambda s: s[0].partition(':')[0])
    ]:
        ccls = BOOTSTRAP_TYPES_BY_NAME[cname].Config
        flds = {f.name: f for f in dc.fields(ccls)}

        kw: ta.Dict[str, ta.Any] = {}
        for aname, aval in cargs:
            k = aname.partition(':')[2]

            if k not in flds:
                k += 's'
                fld = flds[k]

                if fld.type in _or_opt(ta.Sequence[str]):
                    kw.setdefault(k, []).append(aval)

                elif fld.type in _or_opt(ta.Mapping[str, ta.Optional[str]]):
                    if '=' not in aval:
                        kw.setdefault(k, {})[aval] = None
                    else:
                        ek, _, ev = aval.partition('=')
                        kw.setdefault(k, {})[ek] = ev

                elif fld.type in _or_opt(ta.Mapping[int, ta.Union[int, str, None]]):
                    fk, _, fv = aval.partition('=')
                    if not fv:
                        kw.setdefault(k, {})[int(fk)] = None
                    else:
                        kw.setdefault(k, {})[int(fk)] = _int_or_str(fv)

                elif fld.type in _or_opt(ta.Mapping[str, ta.Tuple[ta.Optional[int], ta.Optional[int]]]):
                    fk, _, fv = aval.partition('=')
                    if ',' in fv:
                        tl, tr = fv.split(',')
                    else:
                        tl, tr = None, None
                    kw.setdefault(k, {})[fk] = (_int_or_str(tl) if tl else None, _int_or_str(tr) if tr else None)

                else:
                    raise TypeError(fld)

            else:
                kw[k] = aval

        cfg = ccls(**kw)
        cfgs.append(cfg)

    return cfgs


##


def _main() -> int:
    parser = argparse.ArgumentParser()

    _add_arguments(parser)

    parser.add_argument('-m', '--module', action='store_true')
    parser.add_argument('target')
    parser.add_argument('args', nargs=argparse.REMAINDER)

    args = parser.parse_args()
    cfgs = _process_arguments(args)

    with bootstrap(*cfgs):
        tgt = args.target

        if args.module:
            sys.argv = [tgt, *(args.args or ())]
            runpy._run_module_as_main(tgt)  # type: ignore  # noqa

        else:
            with io.open_code(tgt) as fp:
                src = fp.read()

            ns = dict(
                __name__='__main__',
                __file__=tgt,
                __builtins__=__builtins__,
                __spec__=None,
            )

            import __main__  # noqa
            __main__.__dict__.clear()
            __main__.__dict__.update(ns)
            exec(compile(src, tgt, 'exec'), __main__.__dict__, __main__.__dict__)

        return 0


if __name__ == '__main__':
    sys.exit(_main())
