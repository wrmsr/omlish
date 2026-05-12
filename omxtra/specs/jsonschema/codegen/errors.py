import typing as ta

from omlish import lang


##


SchemaPath: ta.TypeAlias = tuple[str | int, ...]


def format_schema_path(path: SchemaPath) -> str:
    if not path:
        return '/'
    return ''.join(f'/{p}' for p in path)


class JsonSchemaCodeGenError(Exception):
    def __init__(self, *, message: str, path: SchemaPath = ()) -> None:
        super().__init__(message, path)

        self.message = message
        self.path = path

    def __str__(self) -> str:
        if self.path:
            return f'{self.message} at {format_schema_path(self.path)}'
        return self.message


class UnsupportedSchemaError(JsonSchemaCodeGenError, lang.Final):
    pass


class AmbiguousSchemaError(JsonSchemaCodeGenError, lang.Final):
    pass


class UnresolvedRefError(JsonSchemaCodeGenError, lang.Final):
    pass
