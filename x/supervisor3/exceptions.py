class ProcessException(Exception):
    """ Specialized exceptions used when attempting to start a process """


class BadCommand(ProcessException):
    """ Indicates the command could not be parsed properly. """


class NotExecutable(ProcessException):
    """ Indicates that the filespec cannot be executed because its path
    resolves to a file which is not executable, or which is a directory. """


class NotFound(ProcessException):
    """ Indicates that the filespec cannot be executed because it could not be found """


class NoPermission(ProcessException):
    """
    Indicates that the file cannot be executed because the supervisor process does not possess the appropriate UNIX
    filesystem permission to execute the file.
    """
