import typing as ta


DBAPITypeCode: ta.TypeAlias = ta.Any | None

DBAPIColumnDescription: ta.TypeAlias = tuple[
    str,
    DBAPITypeCode,
    int | None,
    int | None,
    int | None,
    int | None,
    bool | None,
]


class DBAPIConnection(ta.Protocol):
    def close(self) -> object: ...

    def commit(self) -> object: ...

    # optional:
    # def rollback(self) -> ta.Any: ...

    def cursor(self) -> 'DBAPICursor': ...


class DBAPICursor(ta.Protocol):
    @property
    def description(self) -> ta.Sequence[DBAPIColumnDescription] | None: ...

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

    def setinputsizes(self, sizes: ta.Sequence[DBAPITypeCode | int | None]) -> object: ...

    def setoutputsize(self, size: int, column: int = ...) -> object: ...
