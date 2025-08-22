async def async_list(fn, *args, **kwargs) -> list:
    """Taken from lang.asyncs"""

    return [v async for v in fn(*args, **kwargs)]


def sync_await(fn, *args, **kwargs):
    """Taken from lang.asyncs"""

    ret = missing = object()

    async def gate():
        nonlocal ret

        ret = await fn(*args, **kwargs)

    cr = gate()
    try:
        try:
            cr.send(None)
        except StopIteration:
            pass

        if ret is missing or cr.cr_await is not None or cr.cr_running:
            raise TypeError('Not terminated')

    finally:
        cr.close()

    return ret


def sync_async_list(fn, *args, **kwargs):
    """Taken from lang.asyncs"""

    lst = None

    async def inner():
        nonlocal lst

        lst = [v async for v in fn(*args, **kwargs)]

    sync_await(inner)

    if not isinstance(lst, list):
        raise TypeError(lst)

    return lst
