# ruff: noqa: UP006 UP007 UP037 UP045
# @omlish-lite
# @omlish-amalg _dumping.py
import json
import os.path
import typing as ta

from omlish.lite.check import check


##


class _DataclassCodegenDumper:
    def __call__(
            self,
            *,
            init_file_path: str,
            out_file_path: str,
    ) -> None:
        from omlish.dataclasses.impl.configs import PACKAGE_CONFIG_CACHE  # noqa
        from omlish.dataclasses.impl.generation.compilation import OpCompiler  # noqa
        from omlish.dataclasses.impl.generation.processor import Codegen  # noqa
        from omlish.dataclasses.impl.generation.processor import GeneratorProcessor  # noqa
        from omlish.dataclasses.impl.processing.base import ProcessingContext  # noqa
        from omlish.dataclasses.impl.processing.driving import processing_options_context  # noqa

        def callback(
                ctx: ProcessingContext,
                prepared: GeneratorProcessor.Prepared,
                comp: OpCompiler.CompileResult,
        ) -> None:
            print(comp)

        #

        processed_modules: ta.List[str] = []

        def process_module(spec: str) -> None:
            processed_modules.append(spec)

            try:
                __import__(spec)
            except ImportError as e:
                # FIXME: include error in output
                print(repr(e))

        def process_dir(dir_path: str) -> None:
            spec = '.'.join(dir_path.split(os.path.sep))

            process_module(spec)

            pkg_cfg = PACKAGE_CONFIG_CACHE.get(spec)
            if pkg_cfg is not None and not pkg_cfg.codegen:
                return

            #

            dns: ta.List[str] = []
            fns: ta.List[str] = []
            for n in os.listdir(dir_path):
                np = os.path.join(dir_path, n)
                if os.path.isdir(np):
                    dns.append(n)
                elif os.path.isfile(np):
                    fns.append(n)

            for fn in sorted(fns):
                if not fn.endswith('.py') or fn == 'conftest.py':
                    continue

                fp = os.path.join(dir_path, fn)

                fpp = fp.split(os.path.sep)
                check.state(fpp[-1].endswith('.py'))
                fpp[-1] = fpp[-1][:-3]
                if fpp[-1] == '__init__':
                    fpp.pop()
                spec = '.'.join(fpp)

                process_module(spec)

            for dn in sorted(dns):
                if dn == 'tests':
                    continue

                dp = os.path.join(dir_path, dn)

                if not os.path.isfile(os.path.join(dp, '__init__.py')):
                    continue

                process_dir(dp)

        #

        with processing_options_context(Codegen(
                style='aot',
                callback=callback,
        )):
            process_dir(os.path.dirname(init_file_path))

        #

        with open(out_file_path, 'w') as f:
            f.write(json.dumps({
                'init_file_path': init_file_path,
                'out_file_path': out_file_path,
                'processed_modules': processed_modules,
            }))
