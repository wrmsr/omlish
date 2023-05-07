import typing as ta

import mypy.plugin as mp
import mypy.types as mt


class PropertiesPlugin(mp.Plugin):

    def get_function_hook(self, fullname: str) -> ta.Optional[ta.Callable[[mp.FunctionContext], mt.Type]]:
        return None
