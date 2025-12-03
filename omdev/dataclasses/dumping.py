# ruff: noqa: UP006 UP007 UP037 UP045
# @omlish-lite
# @omlish-amalg _dumping.py
import json
import os.path

from omlish.lite.check import check


##


class _DataclassCodegenDumper:
    def __call__(
            self,
            *,
            init_file_path: str,
            out_file_path: str,
    ) -> None:
        pkg_dir = os.path.dirname(init_file_path)

        py_files = sorted(
            os.path.join(dn, fn)
            for dn, _, fns in os.walk(pkg_dir)
            for fn in fns
            if fn.endswith('.py')
            if 'tests' not in os.path.split(dn)
            and fn != 'conftest.py'
        )

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
            print(comp.src)

        with processing_options_context(Codegen(callback)):
            for py_file in py_files:
                parts = py_file.split(os.path.sep)
                check.state(parts[-1].endswith('.py'))
                parts[-1] = parts[-1][:-3]
                if parts[-1] == '__init__':
                    parts.pop()

                import_spec = '.'.join(parts)

                # FIXME: terminate on non-codegen config
                try:
                    __import__(import_spec)
                except ImportError as e:
                    # FIXME: include error in output
                    print(repr(e))

        with open(out_file_path, 'w') as f:
            f.write(json.dumps({
                'init_file_path': init_file_path,
                'out_file_path': out_file_path,
            }))
