"""
The fs module's timeline item presenters - tool-specific display knowledge living next to the tools themselves. An
`edit_file` tool card presents as a unified diff of the requested change; the model never sees this (UiText is for
humans), and no frontend knows it exists (they just render whatever the presenters produce).
"""
from ...facades.timelines.items import TimelineItem
from ...facades.timelines.items import ToolUseTimelineItem
from ...facades.timelines.presenting import TimelineItemPresenter
from ...ui.text import DiffUiText
from ...ui.text import UiText


##


class EditFileTimelineItemPresenter(TimelineItemPresenter):
    def present_item(self, item: TimelineItem) -> UiText | None:
        if not isinstance(item, ToolUseTimelineItem):
            return None

        if (use := item.use) is None or use.name != 'edit_file':
            return None

        old = use.args.get('old_string')
        new = use.args.get('new_string')
        if not isinstance(old, str) or not isinstance(new, str):
            return None

        file_path = use.args.get('file_path')

        return UiText.of([
            DiffUiText(
                old=old,
                new=new,
                path=file_path if isinstance(file_path, str) else None,
            ),
        ])
