from ..specs import ClassSpec


##


# def get_dataclass_spec(cls: type) -> ClassSpec:
#     check.isinstance(cls, type)
#     sp = getattr(cls, STD_PARAMS_ATTR)
#     return check.isinstance(sp, SpecDataclassParams).spec


def reflect(cls: type) -> ClassSpec:
    raise NotImplementedError
