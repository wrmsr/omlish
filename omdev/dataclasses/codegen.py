"""
TODO:
 - subdir conf files override parents, codegen those separately, don't duplicate
 - refactor dc gen to just Execute and Codegen
 - need to bubble up imports, preamble, deduped
 - still need plan repr / cmp
 - !! manifests for dataclass config?
  - more sparse / diffuse intent, not package-level
 - _gen subdirs
 - static analyze codegen kwarg if possible
 - assess trie, child pkgs can turn off codegen last-in-wins
 - delegate to subprocess import worker
 - statically find only modules that contain dataclass defs?
  - cache asts?
 - amalg gen payload
 - ignore tests dirs
"""
import ast
import importlib
import inspect
import json
import os.path
import shlex
import sys
import tempfile
import time
import typing as ta

from omlish import check
from omlish import collections as col
from omlish import dataclasses as dc
from omlish import lang
from omlish.dataclasses.impl.configs import PackageConfig
from omlish.dataclasses.impl.generation.compilation import OpCompiler
from omlish.dataclasses.impl.generation.processor import Codegen as CodegenProcessingOption
from omlish.dataclasses.impl.generation.processor import GeneratorProcessor
from omlish.dataclasses.impl.processing.base import ProcessingContext
from omlish.dataclasses.impl.processing.driving import processing_options_context
from omlish.logs import all as logs
from omlish.subprocesses.sync import subprocesses

from ..py.asts.toplevel import TopLevelCall
from ..py.asts.toplevel import analyze_module_top_level


log = logs.get_module_logger(globals())


##


def _find_dir_py_files(dir_path: str) -> list[str]:
    return sorted(
        os.path.join(p, fn)
        for p, dns, fns in os.walk(dir_path)
        for fn in fns
        if fn.endswith('.py')
    )


@lang.cached_function
def _module_manifest_dumper_payload_src() -> str:
    from . import _dumping
    return inspect.getsource(_dumping)


class DataclassCodeGen:
    def __init__(
            self,
            *,
            subprocess_kwargs: ta.Mapping[str, ta.Any] | None = None,
    ) -> None:
        super().__init__()

        self._subprocess_kwargs = subprocess_kwargs

    #

    def run_package_config(
            self,
            pkg_root: str,
            config: PackageConfig,
    ) -> None:
        if not config.codegen:
            return

        log.info(lambda: f'Running codegen on package: {pkg_root}')

        sub_pkgs = sorted(lang.yield_importable(
            pkg_root,
            recursive=True,
        ))

        for sub_pkg in sub_pkgs:
            def callback(
                    ctx: ProcessingContext,
                    prepared: GeneratorProcessor.Prepared,
                    comp: OpCompiler.CompileResult,
            ) -> None:
                print(ctx.cls)
                print(prepared.plans)
                print(comp.src)

            with processing_options_context(CodegenProcessingOption(callback)):
                print(f'{sub_pkg=}')
                try:
                    importlib.import_module(sub_pkg)
                except ImportError as e:
                    print(repr(e))

    #

    @dc.dataclass(frozen=True)
    class ConfiguredPackage:
        name: str

        init_file_path: str
        init_module_name: str

        init_package_call: TopLevelCall

    def scan_py_file(self, file_path: str) -> ConfiguredPackage | None:
        with open(file_path) as f:
            source = f.read()

        module = check.isinstance(ast.parse(source), ast.Module)
        module_name = '.'.join([
            *os.path.dirname(file_path).split(os.path.sep),
            os.path.basename(file_path).removesuffix('.py'),
        ])

        tl = analyze_module_top_level(module, module_name)

        init_calls: list[TopLevelCall] = []
        for call in tl.calls:
            if call.imp.spec != 'omlish.dataclasses':
                continue
            match call.node:
                case ast.Call(func=ast.Attribute(attr='init_package')):
                    init_calls.append(call)

        if not init_calls:
            return None
        if os.path.basename(file_path) != '__init__.py':
            raise ValueError(f'File {file_path} has init_package call and is not an __init__.py: {init_calls!r}')
        if len(init_calls) > 1:
            raise ValueError(f'File {file_path} has multiple init_package calls: {init_calls!r}')

        return DataclassCodeGen.ConfiguredPackage(
            '.'.join(module_name.split('.')[:-1]),
            file_path,
            module_name,
            check.single(init_calls),
        )

    def find_configured_packages(self, root_dirs: ta.Iterable[str]) -> list[ConfiguredPackage]:
        check.not_isinstance(root_dirs, str)

        py_files = (
            fp
            for rd in root_dirs
            for fp in _find_dir_py_files(rd)
        )

        return [
            cfg_pkg
            for file_path in py_files
            if (cfg_pkg := self.scan_py_file(file_path)) is not None
        ]

    #

    def _run_dumper_subprocess(
            self,
            cfg_pkg: ConfiguredPackage,
            dumper_kwargs: ta.Mapping[str, ta.Any],
            *,
            shell_wrap: bool = True,
    ) -> None:
        dumper_payload_src = _module_manifest_dumper_payload_src()

        subproc_src = '\n\n'.join([
            dumper_payload_src,
            f'_DataclassCodegenDumper()(**{dumper_kwargs!r})\n',
        ])

        args = [
            sys.executable,
            '-c',
            subproc_src,
        ]

        if shell_wrap:
            args = ['sh', '-c', ' '.join(map(shlex.quote, args))]

        subprocesses.check_call(
            *args,
            **(self._subprocess_kwargs or {}),
        )

    def _run_dumper_inline(
            self,
            cfg_pkg: ConfiguredPackage,
            dumper_kwargs: ta.Mapping[str, ta.Any],
    ) -> None:
        from . import dumping

        dumping._DataclassCodegenDumper()(**dumper_kwargs)  # noqa

    def process_configured_package(
            self,
            cfg_pkg: ConfiguredPackage,
            *,
            warn_threshold_s: float | None = 10.,
    ) -> None:
        out_dir = tempfile.mkdtemp()
        out_file_path = os.path.join(out_dir, 'output.json')

        dumper_kwargs = dict(
            init_file_path=cfg_pkg.init_file_path,
            out_file_path=out_file_path,
        )

        start_time = time.time()

        # self._run_dumper_subprocess(cfg_pkg, dumper_kwargs)
        self._run_dumper_inline(cfg_pkg, dumper_kwargs)

        end_time = time.time()

        if warn_threshold_s is not None and (elapsed_time := (end_time - start_time)) >= warn_threshold_s:
            log.warning('Dataclass codegen took a long time: %s, %.2f s', cfg_pkg.name, elapsed_time)

        with open(out_file_path) as f:
            out_s = f.read()

        out_dct = json.loads(out_s)
        print(out_dct)

    def run(self, root_dirs: ta.Iterable[str]) -> None:
        check.not_isinstance(root_dirs, str)

        cfg_pkgs = self.find_configured_packages(root_dirs)

        cfg_pkg_trie = col.Trie([  # noqa
            (cfg_pkg.name.split('.'), cfg_pkg)
            for cfg_pkg in cfg_pkgs
        ])

        for cfg_pkg in cfg_pkgs:
            self.process_configured_package(cfg_pkg)
