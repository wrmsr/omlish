class Error(Exception):
    pass


##


class ColumnError(Error):
    pass


class DuplicateColumnNameError(ColumnError):
    pass


class MismatchedColumnCountError(ColumnError):
    pass


##


class QueryError(Error):
    pass
