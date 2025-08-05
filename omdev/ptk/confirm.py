import typing as ta

from prompt_toolkit.formatted_text import merge_formatted_text
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.key_binding import KeyPressEvent
from prompt_toolkit.shortcuts import PromptSession

from omlish import check


##


def create_strict_confirm_session(
        message: str,
        suffix: str = ' (y/n) ',
) -> PromptSession[str | bool]:
    """Create a `PromptSession` object for the 'confirm' function."""

    bindings = KeyBindings()

    @bindings.add('y')
    @bindings.add('Y')
    def yes(event: KeyPressEvent) -> None:
        session.default_buffer.text = 'y'
        event.app.exit(result=True)

    @bindings.add('n')
    @bindings.add('N')
    def no(event: KeyPressEvent) -> None:
        session.default_buffer.text = 'n'
        event.app.exit(result=False)

    complete_message = merge_formatted_text([message, suffix])
    session: PromptSession[str | bool] = PromptSession(
        complete_message,
        key_bindings=bindings,
    )
    return session


##
# TODO: generalize, of course..


# def strict_confirm(message: str = 'Confirm?', suffix: str = ' (y/n) ') -> bool:
#     """Display a confirmation prompt that returns True/False. Requires an explicit answer."""
#
#     while True:
#         session = create_strict_confirm_session(message, suffix)
#         ret = session.prompt()
#
#         if isinstance(ret, str):
#             check.empty(ret)
#
#         elif isinstance(ret, bool):
#             return ret
#
#         else:
#             raise TypeError(ret)


def _strict_confirm(
        *,
        message: str,
        suffix: str,
        prompt_session_fn: ta.Callable[..., ta.Generator[ta.Awaitable, ta.Any, ta.Any]],
) -> ta.Generator[ta.Awaitable, ta.Any, bool]:
    """Display a confirmation prompt that returns True/False. Requires an explicit answer."""

    while True:
        session = create_strict_confirm_session(message, suffix)
        ret = yield from prompt_session_fn(session)

        if isinstance(ret, str):
            check.empty(ret)

        elif isinstance(ret, bool):
            return ret

        else:
            raise TypeError(ret)


def strict_confirm(message: str = 'Confirm?', suffix: str = ' (y/n) ') -> bool:
    def prompt_session_fn(session):
        return session.prompt()
        yield  # type: ignore[unreachable]  # noqa

    g = _strict_confirm(
        message=message,
        suffix=suffix,
        prompt_session_fn=prompt_session_fn,
    )
    try:
        next(g)
    except StopIteration as e:
        return check.isinstance(e.value, bool)
    else:
        raise RuntimeError


async def a_strict_confirm(message: str = 'Confirm?', suffix: str = ' (y/n) ') -> bool:
    def prompt_session_fn(session):
        return (yield session.prompt_async())

    g = _strict_confirm(
        message=message,
        suffix=suffix,
        prompt_session_fn=prompt_session_fn,
    )
    i = None
    while True:
        try:
            a = g.send(i)
        except StopIteration as e:
            return check.isinstance(e.value, bool)
        i = await a
