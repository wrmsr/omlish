class OrmError(Exception):
    pass


class DuplicateIndexValueError(OrmError):
    pass


class FinalFieldModifiedError(OrmError):
    pass
