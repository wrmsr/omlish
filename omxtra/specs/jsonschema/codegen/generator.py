import typing as ta

from omlish.specs import jsonschema as js

from .analysis import JsonSchemaAnalyzer
from .config import JsonSchemaCodeGenConfig
from .rendering import ModuleRenderer
from .transforms import JsonSchemaIrTransformer


##


class JsonSchemaCodeGen:
    def __init__(
            self,
            defs: js.Keywords | ta.Mapping[str, js.Keywords],
            *,
            config: JsonSchemaCodeGenConfig | None = None,
    ) -> None:
        super().__init__()

        self._defs = defs
        self._config = config if config is not None else JsonSchemaCodeGenConfig()

    def build_module(self):
        type_defs = JsonSchemaAnalyzer(self._defs, config=self._config).analyze()
        return JsonSchemaIrTransformer(type_defs).transform()

    def gen_module(self) -> str:
        module = self.build_module()
        return ModuleRenderer(config=self._config).render(module)
