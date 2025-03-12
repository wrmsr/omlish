from ..specs import ClassSpec


##


class ClassAnalysis:
    def __init__(self, cls: type, cs: ClassSpec) -> None:
        super().__init__()

        self._cls = cls
        self._cs = cs

    @property
    def cls(self) -> type:
        return self._cls

    @property
    def cs(self) -> ClassSpec:
        return self._cs
