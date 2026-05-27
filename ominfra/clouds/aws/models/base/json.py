import typing as ta

from .base import ShapeInfo


##


def build_to_json_fn(si: ShapeInfo) -> ta.Callable[[ta.Any], ta.Mapping[str, ta.Any]]:
    raise NotImplementedError


def build_from_json_fn(si: ShapeInfo) -> ta.Callable[[ta.Any], ta.Mapping[str, ta.Any]]:
    raise NotImplementedError
