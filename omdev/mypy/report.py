"""
TODO:
 - alt mode: --output=json, subprocess / tee
 - 'grep' - dumb grep for matches
  - thus custom args
"""
import collections
import dataclasses as dc
import typing as ta

from .debug import install_debug_path_finder
from .debug import run_mypy_main


if ta.TYPE_CHECKING:
    import mypy.build
    import mypy.errors


##


@dc.dataclass(frozen=True, kw_only=True)
class JsonOutputError:
    file: str
    line: int
    column: int
    message: str
    hint: ta.Any | None
    code: str
    severity: str  # 'error' | 'note'


##


def _report_build_result(
        result: 'mypy.build.BuildResult',
) -> None:
    errors: ta.Sequence[mypy.errors.ErrorInfo] = [
        e
        for es in result.manager.errors.error_info_map.values()
        for e in es
    ]
    if errors:
        count_by_code = collections.Counter(
            e.code.code
            for e in errors
            if e.code is not None
        )

        print()
        max_code_len = max(map(len, count_by_code))
        for code, count in sorted(count_by_code.items(), key=lambda kv: -kv[1]):
            print(f'{code.rjust(max_code_len)} : {count}')
        print()


##


def _main() -> None:
    install_debug_path_finder()

    ##

    import mypy.main

    old_run_build = mypy.main.run_build

    def new_run_build(*args, **kwargs):
        ret = old_run_build(*args, **kwargs)
        _report_build_result(ta.cast('mypy.build.BuildResult', ret[0]))
        return ret

    mypy.main.run_build = new_run_build

    ##

    run_mypy_main()


if __name__ == '__main__':
    _main()
