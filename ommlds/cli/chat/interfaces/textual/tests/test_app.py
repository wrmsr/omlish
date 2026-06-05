# ruff: noqa: SLF001
"""
The headless textual e2e: the real ChatApp, really wired (real injector chain, real registry backend resolution, real
driver, real timeline), driven by textual's pilot against the scripted backend - with a gated script making mid-stream
assertions deterministic. Asserts the full input -> driver -> timeline -> widget path: timeline-driven user echo,
streamed thinking + prose widgets observed *while streaming*, finalization, resume-from-window, and clean shutdown.
"""
import pytest

from omdev.tui import textual as tx
from omlish import dataclasses as dc
from omlish import inject as inj

from ...... import minichain as mc
from ......minichain.facades.timelines.tests.harness import PausingGate
from .....backends.configs import BackendConfig
from .....inject import bind_main
from ....configs import ChatConfig
from ....drivers.configs import DriverConfig
from ....drivers.state.configs import StateConfig
from ...textual.app import ChatApp
from ...textual.configs import TextualInterfaceConfig
from ...textual.termrender import BackgroundTerminalRenderer
from ...textual.widgets.messages.ai import StaticAiMessage
from ...textual.widgets.messages.ai import StreamAiMessage
from ...textual.widgets.messages.thinking import StaticThinkingMessage
from ...textual.widgets.messages.thinking import StreamThinkingMessage
from ...textual.widgets.messages.user import UserMessage
from ...textual.widgets.messages.welcome import WelcomeMessage


##


class _NopBackgroundTerminalRenderer(BackgroundTerminalRenderer):
    async def background_render_widget(self, widget, *, no_refresh=False):  # noqa
        pass


async def _pump_until(pilot, fn, n: int = 2_000) -> None:
    for _ in range(n):
        if fn():
            return
        await pilot.pause()

    raise TimeoutError(fn)


def _chat_cfg(db: str | None, new: bool, script: mc.ChatScript) -> ChatConfig:
    return ChatConfig(
        driver=DriverConfig(
            ai=mc.drivers.AiConfig(stream=True),
            # The script rides the real backend-config path into the registry-instantiated scripted backend - as a
            # shared cursor, since that path instantiates a fresh backend per invocation.
            backend=BackendConfig(
                backend='scripted',
                configs=[mc.ScriptedChatCursor(mc.ChatScriptCursor(script))],
            ),
            state=StateConfig(new=new),
            **(dict(orm=mc.drivers.OrmConfig(file_path=db)) if db is not None else {}),  # type: ignore[arg-type]
        ),
        interface=TextualInterfaceConfig(),
    )


def _els(chat_cfg: ChatConfig) -> inj.Elements:
    return inj.as_elements(
        inj.override(
            bind_main(entrypoint_cfg=chat_cfg),

            # Headless: no devtools connection, no primary-buffer scrollback writes.
            inj.bind(tx.DevtoolsSetup, to_const=tx.DevtoolsSetup(lambda app: None)),
            inj.bind(BackgroundTerminalRenderer, to_ctor=_NopBackgroundTerminalRenderer, singleton=True),
        ),
    )


THINKING_TEXT = 'thinking long and hard about all of this'
PROSE_TEXT = 'a **considered** response, streamed in chunks for your viewing pleasure'


@pytest.mark.asyncs('asyncio')
async def test_textual_chat_app_scripted():
    # Pause mid-prose: thinking has fully streamed, prose is partially streamed, nothing is yet canonical.
    gate = PausingGate(lambda pt: pt.invocation_index == 0 and pt.emission_index == 8)

    script = mc.ChatScript(
        [mc.ChatScriptTurn.of(
            mc.ThinkingMessage(THINKING_TEXT),
            mc.AiMessage(PROSE_TEXT),
        )],
        gate=gate,
    )

    async with inj.create_async_managed_injector(_els(_chat_cfg(None, True, script))) as injector:
        app = await injector[ChatApp]

        async with app.run_test() as pilot:
            cdi = app._chat_driver_interface

            await _pump_until(pilot, lambda: bool(app.query(WelcomeMessage)))

            # Send input through the real path: action queue -> facade -> driver -> timeline -> widgets.
            await cdi.send_user_input('hello there')

            # Park mid-stream, deterministically.
            await _pump_until(pilot, lambda: gate.paused)

            # The user echo arrived *from the timeline* (no widget-side echo anymore), and both in-flight stream
            # widgets exist - observed genuinely mid-stream.
            await _pump_until(pilot, lambda: bool(app.query(UserMessage)))
            await _pump_until(pilot, lambda: bool(app.query(StreamThinkingMessage)))
            await _pump_until(pilot, lambda: bool(app.query(StreamAiMessage)))

            (sam,) = app.query(StreamAiMessage)
            assert sam.state == 'streaming'

            gate.resume()

            # Stream completes; canonical replacement finalizes the widgets in place.
            await _pump_until(pilot, lambda: all(
                w.state == 'finalized'
                for w in app.query(StreamAiMessage)
            ))

            (sam,) = app.query(StreamAiMessage)
            assert sam.final_content == PROSE_TEXT

            (stm,) = app.query(StreamThinkingMessage)
            assert stm.state == 'finalized'
            assert stm.final_content == THINKING_TEXT

            await _pump_until(pilot, lambda: cdi.state is cdi.state.IDLE)


@pytest.mark.asyncs('asyncio')
async def test_textual_chat_app_resume(tmp_path):
    """A second app session over the same state db renders the prior conversation from the timeline window."""

    db = str(tmp_path / 'state.db')

    script = mc.ChatScript([
        mc.ChatScriptTurn.of(
            mc.ThinkingMessage(THINKING_TEXT),
            mc.AiMessage(PROSE_TEXT),
        ),
    ])

    # Session one: converse, persist.
    async with inj.create_async_managed_injector(_els(_chat_cfg(db, True, script))) as injector:
        app = await injector[ChatApp]

        async with app.run_test() as pilot:
            cdi = app._chat_driver_interface
            await cdi.send_user_input('remember this')

            await _pump_until(pilot, lambda: any(
                'viewing pleasure' in (w.message_content or '')
                for w in (*app.query(StaticAiMessage), *app.query(StreamAiMessage))
            ))
            await _pump_until(pilot, lambda: cdi.state is cdi.state.IDLE)

    # Session two: resume - the prior turn renders from the attach window, through the same translation as live.
    async with inj.create_async_managed_injector(_els(_chat_cfg(db, False, script))) as injector:
        app = await injector[ChatApp]

        async with app.run_test() as pilot:
            await _pump_until(pilot, lambda: bool(app.query(StaticAiMessage)))

            (um,) = app.query(UserMessage)
            assert 'remember this' in str(um._content)

            (sam,) = app.query(StaticAiMessage)
            assert sam.message_content == PROSE_TEXT

            (stm,) = app.query(StaticThinkingMessage)
            assert stm.message_content == THINKING_TEXT


@pytest.mark.asyncs('asyncio')
async def test_textual_lazy_scrollback(tmp_path):
    """A small initial window plus load_older_items pages history in above the fold."""

    db = str(tmp_path / 'state.db')

    script = mc.ChatScript([
        mc.ChatScriptTurn.of(mc.AiMessage(f'answer number {i}'))
        for i in range(4)
    ])

    # Session one: four turns persisted.
    async with inj.create_async_managed_injector(_els(_chat_cfg(db, True, script))) as injector:
        app = await injector[ChatApp]

        async with app.run_test() as pilot:
            cdi = app._chat_driver_interface
            for i in range(4):
                await cdi.send_user_input(f'question number {i}')
                await _pump_until(pilot, lambda i=i: any(
                    f'answer number {i}' in (w.message_content or '')
                    for w in (*app.query(StaticAiMessage), *app.query(StreamAiMessage))
                ))
            await _pump_until(pilot, lambda: cdi.state is cdi.state.IDLE)

    # Session two: a 3-item initial window, then page the rest in.
    cfg = _chat_cfg(db, False, script)
    cfg = dc.replace(cfg, interface=TextualInterfaceConfig(initial_timeline_window=3))

    async with inj.create_async_managed_injector(_els(cfg)) as injector:
        app = await injector[ChatApp]

        async with app.run_test() as pilot:
            cdi = app._chat_driver_interface

            await _pump_until(pilot, lambda: len(app.query(StaticAiMessage)) >= 1)
            n_before = len(app.query('.message')) - len(app.query(WelcomeMessage))
            assert n_before == 3

            loaded = await cdi.load_older_items(100)
            assert loaded > 0

            await _pump_until(pilot, lambda: len(app.query(UserMessage)) >= 4)

            # Everything is present, in conversation order, with the prepended history above.
            user_texts = [str(w._content) for w in app.query(UserMessage)]
            assert user_texts == [f'question number {i}' for i in range(4)]

            ai_texts = [w.message_content for w in app.query(StaticAiMessage)]
            assert ai_texts == [f'answer number {i}' for i in range(4)]

            # And history is exhausted now.
            assert await cdi.load_older_items(100) == 0
