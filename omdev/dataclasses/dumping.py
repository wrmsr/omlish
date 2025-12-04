# ruff: noqa: UP006 UP007 UP037 UP045
# @omlish-lite
# @omlish-amalg _dumping.py
import dataclasses as dc
import os.path
import typing as ta

from omlish.lite.check import check
from omlish.lite.json import json_dumps_pretty
from omlish.lite.marshal import marshal_obj


##


@dc.dataclass(frozen=True)
class DumpedDataclassCodegen:
    mod_name: str

    cls_module: str
    cls_qualname: str

    plan_repr: str

    fn_name: str
    fn_params: ta.Sequence[str]

    hdr_lines: ta.Sequence[str]
    fn_lines: ta.Sequence[str]

    @dc.dataclass(frozen=True)
    class Ref:
        kind: ta.Literal['op', 'global']
        ident: str

    refs: ta.Sequence[Ref]


@dc.dataclass(frozen=True)
class DataclassCodegenDumperOutput:
    init_file_path: str
    out_file_path: str

    processed_modules: ta.Sequence[str]
    import_errors: ta.Mapping[str, str]

    dumped: ta.Sequence[DumpedDataclassCodegen]


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
        from omlish.dataclasses.impl.generation.globals import FnGlobal  # noqa
        from omlish.dataclasses.impl.generation.ops import OpRef  # noqa
        from omlish.dataclasses.impl.generation.processor import Codegen  # noqa
        from omlish.dataclasses.impl.generation.processor import GeneratorProcessor  # noqa
        from omlish.dataclasses.impl.processing.base import ProcessingContext  # noqa
        from omlish.dataclasses.impl.processing.driving import processing_options_context  # noqa

        cur_module: ta.Optional[str] = None

        dumped: ta.List[DumpedDataclassCodegen] = []

        def callback(
                ctx: ProcessingContext,
                prepared: GeneratorProcessor.Prepared,
                comp: OpCompiler.CompileResult,
        ) -> None:
            d_refs: ta.List[DumpedDataclassCodegen.Ref] = []
            for ref in comp.refs:
                if isinstance(ref, OpRef):
                    d_refs.append(DumpedDataclassCodegen.Ref(
                        kind='op',
                        ident=ref.ident(),
                    ))
                elif isinstance(ref, FnGlobal):
                    d_refs.append(DumpedDataclassCodegen.Ref(
                        kind='global',
                        ident=ref.ident,
                    ))
                else:
                    raise TypeError(ref)

            dumped.append(DumpedDataclassCodegen(
                mod_name=check.not_none(cur_module),

                cls_module=ctx.cls.__module__,
                cls_qualname=ctx.cls.__qualname__,

                plan_repr=repr(prepared.plans),

                fn_name=comp.fn_name,
                fn_params=comp.fn_params,

                hdr_lines=comp.hdr_lines,
                fn_lines=comp.fn_lines,

                refs=d_refs,
            ))

        #

        processed_modules: ta.List[str] = []

        import_errors: ta.Dict[str, str] = {}

        def process_module(spec: str) -> None:
            nonlocal cur_module
            check.none(cur_module)
            cur_module = spec

            try:
                processed_modules.append(spec)

                try:
                    __import__(spec)
                except Exception as e:  # noqa
                    import_errors[spec] = repr(e)

            finally:
                cur_module = None

        def process_dir(dir_path: str) -> None:
            spec = '.'.join(dir_path.split(os.path.sep))

            process_module(spec)

            pkg_cfg = PACKAGE_CONFIG_CACHE.get(spec)
            if pkg_cfg is not None and not pkg_cfg.cfg.codegen:
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
                if not fn.endswith('.py') or fn in ('conftest.py', '_dataclasses.py'):
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
                force=True,
                callback=callback,
        )):
            process_dir(os.path.dirname(init_file_path))

        #

        output = DataclassCodegenDumperOutput(
            init_file_path=init_file_path,
            out_file_path=out_file_path,

            processed_modules=processed_modules,
            import_errors=import_errors,

            dumped=dumped,
        )

        with open(out_file_path, 'w') as f:
            f.write(json_dumps_pretty(marshal_obj(output)))
