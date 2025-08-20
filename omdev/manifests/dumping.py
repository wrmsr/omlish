# ruff: noqa: UP006 UP007 UP037 UP045
# @omlish-lite
# @omlish-amalg _dumping.py
import collections.abc
import dataclasses as dc
import functools
import importlib
import json
import typing as ta

from omlish.lite.cached import cached_nullary
from omlish.lite.marshal import marshal_obj
from omlish.lite.marshal import unmarshal_obj


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

    def _build_manifest_dct(self, manifest: ta.Any) -> ta.Mapping[str, ta.Any]:
        manifest_json = json.dumps(marshal_obj(manifest))
        manifest_dct = json.loads(manifest_json)

        rt_manifest: ta.Any = unmarshal_obj(manifest_dct, type(manifest))
        rt_manifest_json: ta.Any = json.dumps(marshal_obj(rt_manifest))
        rt_manifest_dct: ta.Any = json.loads(rt_manifest_json)
        if rt_manifest_dct != manifest_dct:
            raise Exception(
                f'Manifest failed to roundtrip: '
                f'{manifest} => {manifest_dct} != {rt_manifest} => {rt_manifest_dct}',
            )

        return manifest_dct

    #

    def _load_attr_manifest(self, target: dict) -> dict:
        attr = target['attr']
        manifest = getattr(self._mod(), attr)

        if dc.is_dataclass(manifest):
            # Support static dataclasses
            if isinstance(manifest, type):
                manifest = manifest()

            manifest_dct = self._build_manifest_dct(manifest)

            cls = type(manifest)
            key = f'!{cls.__module__}.{cls.__qualname__}'

            return {key: manifest_dct}

        elif isinstance(manifest, collections.abc.Mapping):
            [(key, manifest_dct)] = manifest.items()
            if not key.startswith('!'):  # noqa
                raise Exception(f'Bad key: {key}')

            if not isinstance(manifest_dct, collections.abc.Mapping):
                raise Exception(f'Bad value: {manifest_dct}')

            manifest_json = json.dumps(manifest_dct)

            rt_manifest_dct = json.loads(manifest_json)
            if rt_manifest_dct != manifest_dct:
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

        manifest_dct = self._build_manifest_dct(manifest)

        key = f'!{cls.__module__}.{cls.__qualname__}'
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
