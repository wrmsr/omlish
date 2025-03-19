"""
TODO:
 - bane
  - owned lock
  - async once

See:
 - https://github.com/davidbrochart/sqlite-anyio/blob/a3ba4c6ef0535b14a5a60071fcd6ed565a514963/sqlite_anyio/sqlite.py
 - https://github.com/rafalkrupinski/ratelimit-anyio/blob/2910a8a3d6fa54ed17ee6ba457686c9f7a4c4beb/src/ratelimit_anyio/__init__.py
 - https://github.com/nekitdev/async-extensions/tree/main/async_extensions
 - https://github.com/kinnay/anynet/tree/master/anynet
 - https://github.com/M-o-a-T/asyncscope
 - https://github.com/M-o-a-T/aevent
 - https://github.com/florimondmanca/aiometer
 - https://github.com/sanitizers/octomachinery/blob/b36c3d3d49da813ac46e361424132955a4e99ac8/octomachinery/utils/asynctools.py

==

async def killer(shutdown: anyio.Event, sleep_s: float) -> None:
    log.warning('Killing in %d seconds', sleep_s)
    await anyio.sleep(sleep_s)
    log.warning('Killing')
    shutdown.set()

"""  # noqa

from .backends import (  # noqa
    BackendTask,
    get_backend_task,
    get_current_backend_task,
)

from .futures import (  # noqa
    FutureError,
    FutureOutcomeAlreadySetError,

    Future,

    create_future,
)

from .signals import (  # noqa
    install_shutdown_signal_handler,
)

from .streams import (  # noqa
    MemoryObjectReceiveStream,
    MemoryObjectSendStream,

    StapledByteStream,
    StapledObjectStream,

    MemoryStapledObjectStream,

    split_memory_object_streams,
    create_stapled_memory_object_stream,
    create_memory_object_stream,
    staple_memory_object_stream,
    staple_memory_object_stream2,
)

from .sync import (  # noqa
    Once,
    Lazy,
    LazyFn,
)

from .utils import (  # noqa
    eof_to_empty,
    gather,
    first,

    get_current_task,

    call_with_task_group,
    run_with_task_group,
)
