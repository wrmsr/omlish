# ruff: noqa: UP006 UP007
import typing as ta


class _ModuleManifestDumper:
    def __init__(self, spec: str) -> None:
        super().__init__()

        self._spec = spec

    def __call__(self, *targets: dict) -> None:
        import collections.abc
        import dataclasses as dc  # noqa
        import functools
        import importlib
        import json

        mod = importlib.import_module(self._spec)

        cls: ta.Any

        out = []
        for target in targets:
            origin = target['origin']

            if target['kind'] == 'attr':
                attr = target['attr']
                manifest = getattr(mod, attr)

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
                    out_value = {key: manifest_dct}

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

                    out_value = {key: manifest_dct}

                else:
                    raise TypeError(f'Manifest must be dataclass or mapping: {manifest!r}')

            elif target['kind'] == 'inline':
                cls = importlib.import_module(target['cls_mod_name'])
                for p in target['cls_qualname'].split('.'):
                    cls = getattr(cls, p)
                if not isinstance(cls, type) or not dc.is_dataclass(cls):
                    raise TypeError(cls)

                cls_fac = functools.partial(cls, **target['kwargs'])
                eval_attr_name = '__manifest_factory__'
                inl_glo = {
                    **mod.__dict__,
                    eval_attr_name: cls_fac,
                }
                inl_src = eval_attr_name + target['init_src']
                inl_code = compile(inl_src, '<magic>', 'eval')
                manifest = eval(inl_code, inl_glo)  # noqa
                manifest_json = json.dumps(dc.asdict(manifest))
                manifest_dct = json.loads(manifest_json)
                key = f'${cls.__module__}.{cls.__qualname__}'
                out_value = {key: manifest_dct}

            else:
                raise ValueError(target)

            out.append({
                **origin,
                'value': out_value,
            })

        out_json = json.dumps(out, indent=None, separators=(',', ':'))
        print(out_json)
