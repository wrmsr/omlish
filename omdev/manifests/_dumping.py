#!/usr/bin/env python3
# noinspection DuplicatedCode
# @omlish-lite
# @omlish-script
# @omlish-generated
# @omlish-amalg-output dumping.py
# @omlish-git-diff-omit
# ruff: noqa: UP006 UP007 UP036 UP037 UP045
import collections.abc
import dataclasses as dc
import functools
import importlib
import json
import sys
import typing as ta


########################################


if sys.version_info < (3, 8):
    raise OSError(f'Requires python (3, 8), got {sys.version_info} from {sys.executable}')  # noqa


########################################


# ../../omlish/lite/cached.py
T = ta.TypeVar('T')
CallableT = ta.TypeVar('CallableT', bound=ta.Callable)


########################################
# ../../../omlish/lite/cached.py


##


class _AbstractCachedNullary:
    def __init__(self, fn):
        super().__init__()
        self._fn = fn
        self._value = self._missing = object()
        functools.update_wrapper(self, fn)

    def __call__(self, *args, **kwargs):  # noqa
        raise TypeError

    def __get__(self, instance, owner):  # noqa
        bound = instance.__dict__[self._fn.__name__] = self.__class__(self._fn.__get__(instance, owner))
        return bound


##


class _CachedNullary(_AbstractCachedNullary):
    def __call__(self, *args, **kwargs):  # noqa
        if self._value is self._missing:
            self._value = self._fn()
        return self._value


def cached_nullary(fn: CallableT) -> CallableT:
    return _CachedNullary(fn)  # type: ignore


def static_init(fn: CallableT) -> CallableT:
    fn = cached_nullary(fn)
    fn()
    return fn


##


class _AsyncCachedNullary(_AbstractCachedNullary):
    async def __call__(self, *args, **kwargs):
        if self._value is self._missing:
            self._value = await self._fn()
        return self._value


def async_cached_nullary(fn):  # ta.Callable[..., T]) -> ta.Callable[..., T]:
    return _AsyncCachedNullary(fn)


########################################
# dumping.py


##


class _ModuleManifestDumper:
    def __init__(
            self,
            spec: str,
            *,
            output: ta.Optional[ta.Callable[[str], None]] = None,
    ) -> None:
        super().__init__()

        self._spec = spec
        if output is None:
            output = print
        self._output = output

    #

    @cached_nullary
    def _mod(self) -> ta.Any:
        return importlib.import_module(self._spec)

    #

    def _load_attr_manifest(self, target: dict) -> dict:
        attr = target['attr']
        manifest = getattr(self._mod(), attr)

        if dc.is_dataclass(manifest):
            # Support static dataclasses
            if isinstance(manifest, type):
                manifest = manifest()

            cls = type(manifest)
            manifest_json = json.dumps(dc.asdict(manifest))
            manifest_dct = json.loads(manifest_json)

            rt_manifest = cls(**manifest_dct)
            if rt_manifest != manifest:
                raise Exception(f'Manifest failed to roundtrip: {manifest} => {manifest_dct} != {rt_manifest}')

            key = f'${cls.__module__}.{cls.__qualname__}'
            return {key: manifest_dct}

        elif isinstance(manifest, collections.abc.Mapping):
            [(key, manifest_dct)] = manifest.items()
            if not key.startswith('$'):  # noqa
                raise Exception(f'Bad key: {key}')

            if not isinstance(manifest_dct, collections.abc.Mapping):
                raise Exception(f'Bad value: {manifest_dct}')

            manifest_json = json.dumps(manifest_dct)
            rt_manifest_dct = json.loads(manifest_json)
            if manifest_dct != rt_manifest_dct:
                raise Exception(f'Manifest failed to roundtrip: {manifest_dct} != {rt_manifest_dct}')

            return {key: manifest_dct}

        else:
            raise TypeError(f'Manifest must be dataclass or mapping: {manifest!r}')

    #

    class _LazyGlobals(dict):
        def __init__(self, get_missing: ta.Callable[[str], ta.Any]) -> None:
            super().__init__()

            self.__get_missing = get_missing

        def __missing__(self, key):
            return self.__get_missing(key)

    def _load_inline_manifest(self, target: dict) -> dict:
        cls: ta.Any = importlib.import_module(target['cls_mod_name'])
        for p in target['cls_qualname'].split('.'):
            cls = getattr(cls, p)
        if not isinstance(cls, type) or not dc.is_dataclass(cls):
            raise TypeError(cls)

        cls_fac = functools.partial(cls, **target['kwargs'])
        eval_attr_name = '__manifest_factory__'

        inl_glo = self._LazyGlobals(lambda k: getattr(self._mod(), k))
        inl_glo.update({
            eval_attr_name: cls_fac,
        })

        inl_src = eval_attr_name + target['init_src']
        inl_code = compile(inl_src, '<magic>', 'eval')
        manifest = eval(inl_code, inl_glo)  # noqa
        manifest_json = json.dumps(dc.asdict(manifest))
        manifest_dct = json.loads(manifest_json)
        key = f'${cls.__module__}.{cls.__qualname__}'
        return {key: manifest_dct}

    #

    def __call__(
            self,
            *targets: dict,  # .build.ManifestDumperTarget
    ) -> None:
        out = []
        for target in targets:
            origin = target['origin']

            if target['kind'] == 'attr':
                out_value = self._load_attr_manifest(target)

            elif target['kind'] == 'inline':
                out_value = self._load_inline_manifest(target)

            else:
                raise ValueError(target)

            out.append({
                **origin,
                'value': out_value,
            })

        out_json = json.dumps(out, indent=None, separators=(',', ':'))
        self._output(out_json)
