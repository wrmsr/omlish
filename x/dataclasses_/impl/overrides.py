from ... import lang
from .fields import field_assign
from .params import get_field_extras
from .processing import Processor
from .utils import create_fn
from .utils import set_new_attribute


class OverridesProcessor(Processor):
    def _process(self) -> None:
        for f in self._info.instance_fields:
            fx = get_field_extras(f)
            if not (fx.override or self._info.params_extras.override):
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
                    [
                        field_assign(
                            self._info.params.frozen,
                            f.name,
                            f.name,
                            self_name,
                            True,
                        ),
                    ],
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
