"""
The offline fizzbuzz e2e: the full agent loop - scripted LLM, *real* fs tools reading and editing a real workspace
file, real permission flow, real storage - with the timeline watching live, all with zero network. The offline sibling
of `drivers/tests/e2e/fixfizzbuzz/`, plus timeline assertions that suite predates.
"""
import os.path
import shutil
import typing as ta

import pytest

from omlish import check
from omlish import inject as inj

from ....backends.scripted.scripts import ChatScript
from ....backends.scripted.scripts import ChatScriptTurn
from ....chat.messages import AiMessage
from ....chat.messages import Message
from ....chat.messages import ToolUseMessage
from ....chat.messages import ToolUseResultMessage
from ....content.render.standard import render_content_str
from ....fs import FsRoot
from ....modules.fs.configs import FsConfig
from ....modules.inject import bind_module
from ....tools.types import ToolUse
from ..items import AiMessageTimelineItem
from ..items import ToolUseTimelineItem
from ..items import ToolUseTimelineItemState
from ..items import UserMessageTimelineItem
from ..presenting import TimelineItemPresenters
from ..presenting import present_timeline_item
from ..translate import translate_chat
from .harness import timeline_driver_harness
from .test_manager import canon_items


##


BUGGY_LINE = 'if i % 3 == 0 and i % 5:'
FIXED_LINE = 'if i % 3 == 0 and i % 5 == 0:'


def _orig_workspace_dir() -> str:
    # Test-only __file__ use, per codestyle.
    return os.path.join(
        os.path.dirname(__file__),
        '..', '..', '..', 'drivers', 'tests', 'e2e', 'fixfizzbuzz', 'workspace',
    )


def _expect_last_tool_result(contains: str) -> ta.Callable[[ta.Sequence[Message]], None]:
    def inner(chat: ta.Sequence[Message]) -> None:
        turm = check.isinstance(chat[-1], ToolUseResultMessage)
        assert contains in render_content_str(turm.tur.c)

    return inner


@pytest.mark.asyncs('asyncio')
async def test_fizzbuzz_offline(tmp_path):
    ws = str(tmp_path / 'workspace')
    shutil.copytree(_orig_workspace_dir(), ws)
    fizz_path = os.path.join(ws, 'fizzbuzz.py')

    script = ChatScript([
        ChatScriptTurn.of(
            AiMessage('Let me read the file first.'),
            ToolUseMessage(ToolUse(
                id='call_read',
                name='read_file',
                args={'file_path': fizz_path},
            )),
        ),
        ChatScriptTurn.of(
            AiMessage('Found it - the FizzBuzz branch tests `i % 5` instead of `i % 5 == 0`. Fixing.'),
            ToolUseMessage(ToolUse(
                id='call_edit',
                name='edit_file',
                args={
                    'file_path': fizz_path,
                    'old_string': BUGGY_LINE,
                    'new_string': FIXED_LINE,
                },
            )),
            expect=_expect_last_tool_result(BUGGY_LINE),  # the read's real output came back around
        ),
        ChatScriptTurn.of(
            AiMessage('The bug is fixed: the first branch now correctly checks divisibility by both 3 and 5.'),
            expect=_expect_last_tool_result('edited successfully'),
        ),
    ])

    async with timeline_driver_harness(
        script,
        enable_tools=True,
        extra_elements=[
            inj.bind(FsRoot, to_const=FsRoot(ws)),
            bind_module(FsConfig()),
        ],
    ) as h:
        await h.send_user_text("There's a bug in the file 'fizzbuzz.py' - can you find and fix it?")

        # The actual file on the actual filesystem is actually fixed.
        with open(fizz_path) as f:  # noqa
            fixed = f.read()
        assert FIXED_LINE in fixed
        assert BUGGY_LINE not in fixed

        # The timeline watched the whole loop.
        items = h.manager.state.get_items()
        assert [type(it) for it in items] == [
            UserMessageTimelineItem,
            AiMessageTimelineItem,
            ToolUseTimelineItem,
            AiMessageTimelineItem,
            ToolUseTimelineItem,
            AiMessageTimelineItem,
        ]

        read_tool, edit_tool = (it for it in items if isinstance(it, ToolUseTimelineItem))
        assert check.not_none(read_tool.use).name == 'read_file'
        assert check.not_none(edit_tool.use).name == 'edit_file'
        assert read_tool.state is edit_tool.state is ToolUseTimelineItemState.COMPLETE
        assert all(t.finalized and t.result is not None for t in (read_tool, edit_tool))
        assert BUGGY_LINE in render_content_str(check.not_none(read_tool.result).c)
        assert 'edited successfully' in render_content_str(check.not_none(edit_tool.result).c)

        # And, of course, convergence.
        assert canon_items(items) == canon_items(translate_chat(await h.storage.get_chat()))

        # The fs module contributed an item presenter: the edit tool card presents as a unified diff.
        presenters = await h.injector[TimelineItemPresenters]
        diff_text = check.not_none(present_timeline_item(presenters, edit_tool))
        diff_str = str(diff_text)
        assert f'-{BUGGY_LINE}' in diff_str
        assert f'+{FIXED_LINE}' in diff_str
        assert present_timeline_item(presenters, read_tool) is None  # nothing special for reads
