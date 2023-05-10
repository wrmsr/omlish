import functools
import typing as ta

from ... import check
from ... import properties
from ..types import Checker
from ..types import CheckException
from ..types import ExtraFieldParams
from ..types import Validator
from ..validation import build_default_field_validation
from .bootstrap import Fields
from .types import Aspect
from .types import attach
from .utils import get_flat_fn_args
from .utils import fn_has_descriptor


class Validation(Aspect):

    @property
    def deps(self) -> ta.Collection[ta.Type[Aspect]]:
        return [Fields]

    @staticmethod
    def raise_check_exception(chk, chk_args, *args):
        if len(chk_args) != len(args):
            raise TypeError(chk_args, args)
        raise CheckException({k: v for k, v in zip(chk_args, args)}, chk)

    @attach(Aspect.Function)
    class Building(Aspect.Function['Validation']):

        def __init__(self, *args, **kwargs) -> None:
            super().__init__(*args, **kwargs)

            self._loaded_fields: ta.Dict[str, str] = {}
            self._cls_name: ta.Optional[str] = None

        @properties.cached
        def fns(self) -> ta.AbstractSet[ta.Callable]:
            return {
                *[vld.fn for vld in self.fctx.ctx.spec.rmro_extras_by_cls[Validator]],
                *[chk.fn for chk in self.fctx.ctx.spec.rmro_extras_by_cls[Checker]],
            }

        def build_cls_lines(self) -> ta.List[str]:
            check.none(self._cls_name)
            ret = []
            if any(fn_has_descriptor(fn) for fn in self.fns):
                self._cls_name = self.fctx.nsb.put(None, 'cls')
                ret.append(f'{self._cls_name} = {self.fctx.self_name}.__class__')
            return ret

        def load_field(self, field: str, lines: ta.List[str]) -> str:
            try:
                return self._loaded_fields[field]
            except KeyError:
                name = self._loaded_fields[field] = self.fctx.nsb.put(None, field)
                lines.append(f'{name} = {self.fctx.self_name}.{field}')
                return name

        def load_fields(
                self,
                wanted: ta.Iterable[str],
                given: ta.AbstractSet[str],
                lines: ta.List[str],
        ) -> ta.Mapping[str, str]:
            dct = {}
            for field in wanted:
                check.in_(field, self.fctx.ctx.spec.fields.by_name)
                if field in given:
                    dct[field] = field
                else:
                    dct[field] = self.load_field(field, lines)
            return dct

        def build_validate_lines(self, fields: ta.AbstractSet[str]) -> ta.List[str]:
            ret = []
            for fld in self.fctx.ctx.spec.fields:
                if fld.name not in fields:
                    continue
                vld_md = fld.metadata.get(ExtraFieldParams, ExtraFieldParams()).validate
                if callable(vld_md):
                    ret.append(f'{self.fctx.nsb.put(vld_md)}({fld.name})')
                elif vld_md is True or (vld_md is None and self.fctx.ctx.extra_params.validate is True):
                    ret.append(f'{self.fctx.nsb.put(build_default_field_validation(fld))}({fld.name})')
                elif vld_md is False or vld_md is None:
                    pass
                else:
                    raise TypeError(vld_md)
            return ret

        def build_validator_lines(self, fields: ta.AbstractSet[str]) -> ta.List[str]:
            ret = []
            for vld in self.fctx.ctx.spec.rmro_extras_by_cls[Validator]:
                vld_args = get_flat_fn_args(vld.fn)
                if not any(arg in fields for arg in vld_args):
                    continue
                fn = self.fctx.nsb.put(vld.fn)
                if fn_has_descriptor(vld.fn):
                    fn = f'{fn}.__get__(None, {check.not_none(self._cls_name)})'
                ldct = self.load_fields(vld_args, fields, ret)
                ret.append(f'{fn}({", ".join(ldct[a] for a in vld_args)})')
            return ret

        def build_check_lines(self, fields: ta.AbstractSet[str]) -> ta.List[str]:
            ret = []
            for fld in self.fctx.ctx.spec.fields:
                if fld.name not in fields:
                    continue
                chk_md = fld.metadata.get(ExtraFieldParams, ExtraFieldParams()).check
                chk_ty_md = fld.metadata.get(ExtraFieldParams, ExtraFieldParams()).check_type
                if chk_ty_md is not None:
                    # FIXME: dedupe against check._unpack_bullshit
                    if isinstance(chk_ty_md, tuple) and None in chk_ty_md:
                        chk_ty_md = tuple(filter(None, chk_ty_md)) + (type(None),)
                    isinstance(None, chk_ty_md)  # noqa
                    bound_build_chk_exc = functools.partial(self.aspect.raise_check_exception, chk_ty_md, [fld.name])
                    ret.append(
                        f'if not {self.fctx.nsb.put(isinstance)}({fld.name}, {self.fctx.nsb.put(chk_ty_md)}): '
                        f'{self.fctx.nsb.put(bound_build_chk_exc)}({fld.name})'
                    )
                if callable(chk_md):
                    bound_build_chk_exc = functools.partial(self.aspect.raise_check_exception, chk_md, [fld.name])
                    ret.append(
                        f'if not {self.fctx.nsb.put(chk_md)}({fld.name}): '
                        f'{self.fctx.nsb.put(bound_build_chk_exc)}({fld.name})'
                    )
                elif chk_md is False or chk_md is None:
                    pass
                else:
                    raise TypeError(chk_md)
            return ret

        def build_checker_lines(self, fields: ta.AbstractSet[str]) -> ta.List[str]:
            ret = []
            for chk in self.fctx.ctx.spec.rmro_extras_by_cls[Checker]:
                chk_args = get_flat_fn_args(chk.fn)
                if not any(arg in fields for arg in chk_args):
                    continue
                fn = self.fctx.nsb.put(chk.fn)
                if fn_has_descriptor(chk.fn):
                    fn = f'{fn}.__get__(None, {check.not_none(self._cls_name)})'
                ldct = self.load_fields(chk_args, fields, ret)
                bound_build_chk_exc = functools.partial(self.aspect.raise_check_exception, chk, chk_args)
                ret.append(
                    f'if not {fn}({", ".join(ldct[a] for a in chk_args)}): '
                    f'{self.fctx.nsb.put(bound_build_chk_exc)}({", ".join(ldct[a] for a in chk_args)})'
                )
            return ret

        def build_validation_lines(self, fields: ta.AbstractSet[str]) -> ta.List[str]:
            return [
                *self.build_cls_lines(),
                *self.build_validate_lines(fields),
                *self.build_validator_lines(fields),
                *self.build_check_lines(fields),
                *self.build_checker_lines(fields),
            ]

    @attach('init')
    class Init(Aspect.Function['Validation']):

        @attach(Aspect.Function.Phase.VALIDATE)
        def build_validation_lines(self) -> ta.List[str]:
            all_fields = set(self.fctx.ctx.spec.fields.by_name)
            return self.fctx.get_aspect(Validation.Building).build_validation_lines(all_fields)

    @attach('pre_set')
    class PreSet(Aspect.Function['Validation']):

        @attach(Aspect.Function.Phase.VALIDATE)
        def build_validation_lines(self) -> ta.List[str]:
            return self.fctx.get_aspect(Validation.Building).build_validation_lines({self.fctx.field.name})
