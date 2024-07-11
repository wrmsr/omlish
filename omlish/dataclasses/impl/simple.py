import inspect

from ... import lang
from .fields import field_assign
from .init import get_init_fields
from .params import get_field_extras
from .processing import Processor
from .utils import create_fn
from .utils import set_new_attribute


class OverridesProcessor(Processor):
    def _process(self) -> None:
        for f in self._info.instance_fields:
            fx = get_field_extras(f)
            if not fx.override:
                continue

            if self._info.params.slots:
                raise TypeError

            self_name = '__dataclass_self__' if 'self' in self._info.fields else 'self'

            getter = create_fn(
                f.name,
                (self_name,),
                [f'return {self_name}.__dict__[{f.name!r}]'],
                globals=self._info.globals,
                return_type=lang.just(f.type),
            )
            prop = property(getter)

            if not self._info.params.frozen:
                setter = create_fn(
                    f.name,
                    (self_name, f'{f.name}: __dataclass_type_{f.name}__'),
                    [field_assign(self._info.params.frozen, f.name, f.name, self_name, fx.override)],
                    globals=self._info.globals,
                    locals={f'__dataclass_type_{f.name}__': f.type},
                    return_type=lang.just(None),
                )
                prop = prop.setter(setter)

            set_new_attribute(
                self._cls,
                f.name,
                prop,
            )


class EqProcessor(Processor):
    def _process(self) -> None:
        if not self._info.params.eq:
            return

        # flds = [f for f in self._info.instance_fields if f.compare]
        # self_tuple = tuple_str('self', flds)
        # other_tuple = tuple_str('other', flds)
        # set_new_attribute(cls, '__eq__', _cmp_fn('__eq__', '==', self_tuple, other_tuple, globals=globals))
        cmp_fields = (field for field in self._info.instance_fields if field.compare)
        terms = [f'self.{field.name} == other.{field.name}' for field in cmp_fields]
        field_comparisons = ' and '.join(terms) or 'True'
        body = [
            f'if self is other:',
            f' return True',
            f'if other.__class__ is self.__class__:',
            f' return {field_comparisons}',
            f'return NotImplemented',
        ]
        func = create_fn('__eq__', ('self', 'other'), body, globals=self._info.globals)
        set_new_attribute(self._cls, '__eq__', func)


class DocProcessor(Processor):
    def _process(self) -> None:
        if getattr(self._cls, '__doc__'):
            return

        try:
            text_sig = str(inspect.signature(self._cls)).replace(' -> None', '')
        except (TypeError, ValueError):
            text_sig = ''
        self._cls.__doc__ = (self._cls.__name__ + text_sig)


class MatchArgsProcessor(Processor):
    def _process(self) -> None:
        if not self._info.params.match_args:
            return

        ifs = get_init_fields(self._info.fields.values())
        set_new_attribute(self._cls, '__match_args__', tuple(f.name for f in ifs.std))
