"""
TODO:
 - subdir conf files override parents, codegen those separately, don't duplicate
 - refactor dc gen to just Execute and Codegen
 - need to bubble up imports, preamble, deduped
 - still need plan repr / cmp
 - !! manifests for dataclass config?
  - more sparse / diffuse intent, not package-level
"""
import importlib
import os.path
import typing as ta

from omlish import check
from omlish import collections as col
from omlish import lang
from omlish.dataclasses.impl.configs import PackageConfig
from omlish.dataclasses.impl.generation.compilation import OpCompiler
from omlish.dataclasses.impl.generation.processor import Codegen as CodegenProcessingOption
from omlish.dataclasses.impl.generation.processor import GeneratorProcessor
from omlish.dataclasses.impl.processing.base import ProcessingContext
from omlish.dataclasses.impl.processing.driving import processing_options_context
from omlish.logs import all as logs


log = logs.get_module_logger(globals())


##


class DataclassCodeGen:
    def __init__(self) -> None:
        super().__init__()

    def run_package_config(
            self,
            pkg_root: str,
            config: PackageConfig,
    ) -> None:
        if not config.codegen:
            return

        log.info('Running codegen on package: %s', pkg_root)

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

    def build_config_trie(
            self,
            root_dirs: ta.Iterable[str],
    ) -> col.Trie[str, PackageConfig]:
        check.not_isinstance(root_dirs, str)

        trie: col.Trie[str, PackageConfig] = col.Trie()
        for root_dir in root_dirs:
            for dp, _, fns in os.walk(root_dir):  # noqa
                # if PACKAGE_CONFIG_FILE_NAME in fns:
                #     with open(os.path.join(dp, PACKAGE_CONFIG_FILE_NAME)) as f:
                #         config = PackageConfig.loads(f.read())
                #     pkg_parts = dp.split(os.sep)
                #     trie[pkg_parts] = config
                pass

        return trie

    def run(
            self,
            root_dirs: ta.Iterable[str],
    ) -> None:
        check.not_isinstance(root_dirs, str)

        config_trie = self.build_config_trie(root_dirs)

        for pkg_parts, pkg_config in config_trie.iteritems(sort_children=True):
            self.run_package_config('.'.join(pkg_parts), pkg_config)
