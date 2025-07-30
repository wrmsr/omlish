# ruff: noqa: UP006 UP007 UP043 UP045
# @omlish-lite
"""
TODO:
 - inject
 - multi-exec - maybe like hyphen separated?
  - explicitly argless / argful?
 - agnostic to '_' / '-' for convenience (like argparse)
 - 'do' def? chain call a task without reexecuting process
"""
import argparse
import os.path
import typing as ta

from omlish.formats.toml.parser import toml_loads
from omlish.funcs.builders import DebugFnBuilder  # noqa
from omlish.funcs.builders import FnBuilder
from omlish.funcs.builders import SimpleFnBuilder  # noqa
from omlish.lite.marshal import unmarshal_obj

from ._marshal import _install_doer_marshaling
from .configs import DoerConfig
from .configs import DoerDefConfig
from .configs import DoerTaskConfig
from .execution import DoerDefExecutor
from .execution import make_doer_def_executor
from .execution import make_doer_task_executor


##


def _main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--config')
    parser.add_argument('task')
    args, task_argv = parser.parse_known_args()

    #

    config_path = args.config
    if config_path is None:
        config_path = os.path.join(os.path.dirname(__file__), 'do.toml')
    with open(config_path) as f:
        config_obj = toml_loads(f.read())['do']

    _install_doer_marshaling()

    task_cfg_objs = config_obj.pop('task', {})
    def_cfg_objs = config_obj.pop('def', {})
    doer_cfg: DoerConfig = unmarshal_obj(config_obj, DoerConfig)

    #

    fn_builder: FnBuilder
    # fn_builder = SimpleFnBuilder()
    fn_builder = DebugFnBuilder()

    #

    ns: dict = {}

    #

    def do_task(task_name: str, *task_argv: str) -> None:
        task_cfg_obj = task_cfg_objs[task_name]
        task_cfg: DoerTaskConfig = unmarshal_obj(task_cfg_obj, DoerTaskConfig)

        task_exe = make_doer_task_executor(
            task_cfg,
            ns=ns,
            doer_config=doer_cfg,
            fn_builder=fn_builder,
        )

        task_exe.execute(*task_argv)

    ns['do'] = do_task

    #

    def def_executor_closure(def_name: str) -> ta.Callable[..., ta.Any]:  # noqa
        def_exe: ta.Optional[DoerDefExecutor] = None

        def inner(*args, **kwargs):
            nonlocal def_exe
            if def_exe is None:
                def_cfg_obj = def_cfg_objs[def_name]
                def_cfg: DoerDefConfig = unmarshal_obj(def_cfg_obj, DoerDefConfig)
                def_exe = make_doer_def_executor(
                    def_cfg,
                    ns=ns,
                    doer_config=doer_cfg,
                    fn_builder=fn_builder,
                )

            return def_exe.execute(*args, **kwargs)

        return inner

    for def_name in def_cfg_objs:
        ns[def_name] = def_executor_closure(def_name)

    #

    do_task(args.task, *task_argv)


if __name__ == '__main__':
    _main()
