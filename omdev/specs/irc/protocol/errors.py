class Error(Exception):
    pass


class LineEmptyError(Error):
    pass


class BadCharactersError(Error):
    pass


class TagsTooLongError(Error):
    pass


class InvalidTagContentError(Error):
    pass


class CommandMissingError(Error):
    pass


class BadParamError(Error):
    pass


class MalformedNuhError(Error):
    pass
