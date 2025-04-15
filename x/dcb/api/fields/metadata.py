import typing as ta

from omlish import lang


##


class _ExtraParams(lang.Marker):
    pass


def extra_field_params(**kwargs) -> ta.Mapping[ta.Any, ta.Any]:
    return {_ExtraParams: kwargs}
