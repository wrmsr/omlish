class ProtocolError(Exception):
    """Raised by the state machine when the IRC protocol is being violated."""

    def __init__(self, message: str) -> None:
        super().__init__(f'IRC protocol violation: {message}')


class UnknownCommandError(ProtocolError):
    """Raised by the state machine when an unrecognized command has been received."""

    def __init__(self, command: str) -> None:
        super().__init__(f'unknown command: {command}')
