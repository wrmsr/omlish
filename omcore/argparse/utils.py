import argparse
import dataclasses as dc
import typing as ta


##


class NoExitArgumentParser(argparse.ArgumentParser):
    def __init__(
            self,
            *args: ta.Any,
            exit_on_error: bool = False,
            **kwargs: ta.Any,
    ) -> None:
        if exit_on_error:
            raise TypeError('exit_on_error=True not supported')

        super().__init__(*args, exit_on_error=False, **kwargs)  # type: ignore[misc]

    @dc.dataclass()
    class ExitNotSupportedError(BaseException):
        status: int
        message: str | None

    def exit(self, status=0, message=None):
        raise self.ExitNotSupportedError(status, message)
