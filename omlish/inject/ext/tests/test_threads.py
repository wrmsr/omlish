from ...bindings import bind
from ...injector import create_injector
from ..threads import bind_thread_locals
from ..threads import thread_local


def test_threads():
    i = create_injector(bind(
        thread_local(420),
        bind_thread_locals(),
    ))
    assert i[int] == 420
