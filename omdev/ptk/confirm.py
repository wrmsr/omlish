
from prompt_toolkit.formatted_text import merge_formatted_text
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.key_binding import KeyPressEvent
from prompt_toolkit.shortcuts import PromptSession

from omlish import check
from omlish import lang


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


def _m_strict_confirm(message: str = 'Confirm?', suffix: str = ' (y/n) ') -> lang.MaysyncGen[bool]:
    """Display a confirmation prompt that returns True/False. Requires an explicit answer."""

    while True:
        session = create_strict_confirm_session(message, suffix)
        ret = (yield lang.maysync_op(session.prompt, session.prompt_async))

        if isinstance(ret, str):
            check.empty(ret)

        elif isinstance(ret, bool):
            return ret

        else:
            raise TypeError(ret)


strict_confirm = lang.maysync_wrap(_m_strict_confirm)
a_strict_confirm = lang.a_maysync_wrap(_m_strict_confirm)
