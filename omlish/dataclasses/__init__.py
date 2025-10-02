# ruff: noqa: I001
import sys as _sys

from .. import lang as _lang


with _lang.auto_proxy_init(globals()) as _api_cap:
    ##

    ##
    # stdlib interface

    from dataclasses import (  # noqa
        FrozenInstanceError,

        MISSING,
        KW_ONLY,

        InitVar,
        Field,

        field,

        dataclass,
        make_dataclass,

        fields,

        is_dataclass,

        replace,
    )

    from .tools.as_ import (  # noqa
        asdict,
        astuple,
    )

    ##
    # additional interface

    from .impl.api.classes.decorator import (  # noqa
        dataclass as xdataclass,
    )

    from .impl.api.classes.make import (  # noqa
        make_dataclass as xmake_dataclass,
    )

    from .impl.api.classes.metadata import (  # noqa
        append_class_metadata,
        extra_class_params,
        init,
        metadata,
        validate,
    )

    from .impl.api.fields.metadata import (  # noqa
        extra_field_params,
        set_field_metadata,
        update_extra_field_params,
        with_extra_field_params,
    )

    from .impl.api.fields.constructor import (  # noqa
        field as xfield,
    )

    from .impl.concerns.replace import (  # noqa
        replace as xreplace,
    )

    from .impl.configs import (  # noqa
        init_package,
    )

    from .errors import (  # noqa
        FieldFnValidationError,
        FieldTypeValidationError,
        FieldValidationError,
        FnValidationError,
        TypeValidationError,
        ValidationError,
    )

    from .metaclass.bases import (  # noqa
        Box,
        Case,
        Data,
        Frozen,
    )

    from .metaclass.meta import (  # noqa
        DataMeta,
    )

    from .metaclass.specs import (  # noqa
        get_metaclass_spec,
    )

    from .reflection import (  # noqa
        reflect,
    )

    from .specs import (  # noqa
        CoerceFn,
        ValidateFn,
        ReprFn,

        InitFn,
        ClassValidateFn,

        DefaultFactory,

        FieldType,

        FieldSpec,

        ClassSpec,
    )

    from .tools.iter import (  # noqa
        fields_dict,

        iter_items,
        iter_keys,
        iter_values,
    )

    from .tools.modifiers import (  # noqa
        field_modifier,
        update_fields,
    )

    from .tools.only_ import (  # noqa
        only,
    )

    from .tools.replace import (  # noqa
        deep_replace,
    )

    from .tools.repr import (  # noqa
        opt_repr,
        truthy_repr,
    )

    from .tools.static import (  # noqa
        Static,
    )

    ##
    # lite imports

    from ..lite.dataclasses import (  # noqa
        dataclass_shallow_asdict as shallow_asdict,
        dataclass_shallow_astuple as shallow_astuple,

        is_immediate_dataclass,

        dataclass_maybe_post_init as maybe_post_init,

        dataclass_descriptor_method as descriptor_method,
    )


##
# globals hack

def _self_patching_global_proxy(l, r, ak_fn=None):
    def inner(*args, **kwargs):
        fn = getattr(_sys.modules[__name__], r)
        globals()[l] = fn
        if ak_fn:
            args, kwargs = ak_fn(*args, **kwargs)
        return fn(*args, **kwargs)
    return inner


globals()['field'] = _self_patching_global_proxy('field', 'xfield')

globals()['dataclass'] = _self_patching_global_proxy('dataclass', 'xdataclass')

globals()['make_dataclass'] = _self_patching_global_proxy(
    'make_dataclass',
    'xmake_dataclass',
    lambda *args, _frame_offset=1, **kwargs: (args, dict(_frame_offset=_frame_offset + 1, **kwargs)),
)

globals()['replace'] = _self_patching_global_proxy('replace', 'xreplace')


_api_cap.update_exports()
del _api_cap
