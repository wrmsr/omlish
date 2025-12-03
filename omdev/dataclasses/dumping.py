# ruff: noqa: UP006 UP007 UP037 UP045
# @omlish-lite
# @omlish-amalg _dumping.py
import json
import typing as ta

from omlish.lite.check import check


##


class _DataclassCodegenDumper:
    def __call__(
            self,
            *,
            import_specs: ta.Sequence[str],
            out_file_path: str,
    ) -> None:
        check.not_isinstance(import_specs, str)

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
            for import_spec in import_specs:
                try:
                    __import__(import_spec)
                except ImportError as e:
                    # FIXME: include error in output
                    print(repr(e))

        with open(out_file_path, 'w') as f:
            f.write(json.dumps({
                'import_specs': import_specs,
                'out_file_path': out_file_path,
            }))
