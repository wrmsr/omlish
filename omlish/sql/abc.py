"""
https://peps.python.org/pep-0249/
"""
import typing as ta


DbapiTypeCode: ta.TypeAlias = ta.Any | None

DbapiColumnDescription: ta.TypeAlias = tuple[
    str,  # name
    DbapiTypeCode,  # type_code
    int | None,  # display_size
    int | None,  # internal_size
    int | None,  # precision
    int | None,  # scale
    bool | None,  # null_ok
]


class DbapiColumnDescription_(ta.NamedTuple):  # noqa
    name: str
    type_code: DbapiTypeCode
    display_size: int | None
    internal_size: int | None
    precision: int | None
    scale: int | None
    null_ok: bool | None


class DbapiConnection(ta.Protocol):
    def close(self) -> object: ...

    def commit(self) -> object: ...

    # optional:
    # def rollback(self) -> ta.Any: ...

    def cursor(self) -> 'DbapiCursor': ...


class DbapiCursor(ta.Protocol):
    @property
    def description(self) -> ta.Sequence[DbapiColumnDescription] | None: ...

    @property
    def rowcount(self) -> int: ...

    # optional:
    # def callproc(self, procname: str, parameters: Sequence[ta.Any] = ...) -> Sequence[ta.Any]: ...

    def close(self) -> object: ...

    def execute(
        self,
        operation: str,
        parameters: ta.Sequence[ta.Any] | ta.Mapping[str, ta.Any] = ...,
    ) -> object: ...

    def executemany(
        self,
        operation: str,
        seq_of_parameters: ta.Sequence[ta.Sequence[ta.Any]],
    ) -> object: ...

    def fetchone(self) -> ta.Sequence[ta.Any] | None: ...

    def fetchmany(self, size: int = ...) -> ta.Sequence[ta.Sequence[ta.Any]]: ...

    def fetchall(self) -> ta.Sequence[ta.Sequence[ta.Any]]: ...

    # optional:
    # def nextset(self) -> None | Literal[True]: ...

    arraysize: int

    def setinputsizes(self, sizes: ta.Sequence[DbapiTypeCode | int | None]) -> object: ...

    def setoutputsize(self, size: int, column: int = ...) -> object: ...
