"""
Item presenters: injectable, frontend-agnostic translation of timeline items into user-facing `UiText` - the place
tool-specific display knowledge (e.g. rendering an edit as a diff) lives, next to neither the frontends nor the
timeline core. Modules contribute presenters for their own tools (see `modules/fs`); frontends ask the presenters
first and fall back to their generic rendering.

Presenters return None for items they don't speak for; the first non-None wins. They are pure display functions over
item values - synchronous, effect-free, and never seen by the model (UiText is for humans; `Content` is for models).
"""
import abc
import typing as ta

from omcore import lang

from ...ui.text import UiText
from .items import TimelineItem


##


class TimelineItemPresenter(lang.Abstract):
    @abc.abstractmethod
    def present_item(self, item: TimelineItem) -> UiText | None:
        raise NotImplementedError


TimelineItemPresenters = ta.NewType('TimelineItemPresenters', ta.Sequence[TimelineItemPresenter])


def present_timeline_item(
        presenters: ta.Iterable[TimelineItemPresenter] | None,
        item: TimelineItem,
) -> UiText | None:
    for p in presenters or ():
        if (t := p.present_item(item)) is not None:
            return t

    return None
