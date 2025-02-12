"""
TODO:
 - put in proper test - need like @pytest.mark.no_threads - handle pycharm/pydevd interference
"""
import json
import os
import sys

from ...lite.json import json_dumps_compact
from ..forkhooks import get_fork_depth
from ..temp import make_temp_file


##


def _main() -> None:
    out_file = make_temp_file()

    def run(*ns: int) -> None:
        obj = {'pid': os.getpid(), 'depth': get_fork_depth()}
        obj_json = json_dumps_compact(obj)

        print(obj_json)

        with open(out_file, 'a') as f:
            f.write(obj_json + '\n')

        for _ in range(ns[0] if ns else 0):
            if not (child_pid := os.fork()):  # noqa
                run(*ns[1:])
                sys.exit(0)

            os.waitpid(child_pid, 0)

    run(2, 2)

    with open(out_file) as f:
        lines = f.readlines()
    objs = [json.loads(sl) for l in lines if (sl := l.strip())]

    obj_depths = [obj['depth'] for obj in objs]
    assert obj_depths == [0, 1, 2, 2, 1, 2, 2]


if __name__ == '__main__':
    _main()
