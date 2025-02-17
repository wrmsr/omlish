# ruff: noqa: UP006 UP007
import dataclasses as dc
import typing as ta


@dc.dataclass(frozen=True)
class ModAttrManifest:
    mod_name: str
    attr_name: str

    def load(self) -> ta.Any:
        importlib = __import__('importlib')
        mod = importlib.import_module(self.mod_name)
        return getattr(mod, self.attr_name)
