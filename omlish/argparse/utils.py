import argparse
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

    def exit(self, status=0, message=None):
        raise TypeError('NoExitArgumentParser.exit() not supported')
