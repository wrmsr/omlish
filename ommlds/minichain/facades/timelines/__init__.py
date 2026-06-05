# fmt: off
# ruff: noqa: I001
from omlish import dataclasses as _dc  # noqa


_dc.init_package(
    globals(),
    codegen=True,
)


##


from omlish import lang as _lang  # noqa


with _lang.auto_proxy_init(globals()):
    ##

    from .events import (  # noqa
        TimelineEvent,

        TimelineItemAppendedEvent,
        TimelineItemUpdatedEvent,
        TimelineItemDeltaEvent,
    )

    from .history import (  # noqa
        LIVE_TIMELINE_CURSOR_REALM,
        STORAGE_TIMELINE_CURSOR_REALM,

        TimelineCursor,
        TimelineCursorError,
        UnresolvableTimelineCursorError,

        TimelineWindow,
        EMPTY_TIMELINE_WINDOW,

        TimelineHistory,
        StateTimelineHistory,
        StorageTimelineHistory,
        CompositeTimelineHistory,
    )

    from .items import (  # noqa
        TimelineId,
        TimelineItemId,

        TimelineItem,

        UserMessageTimelineItem,
        AiMessageTimelineItem,
        ThinkingTimelineItem,
        MessageTimelineItem,

        AiStreamTimelineItem,
        ThinkingStreamTimelineItem,

        ToolUseTimelineItemState,
        ToolUseTimelineItem,

        UiMessageTimelineItem,
        ErrorTimelineItem,
    )

    from .manager import (  # noqa
        TimelineManager,
    )

    from .presenting import (  # noqa
        TimelineItemPresenter,
        TimelineItemPresenters,
        present_timeline_item,
    )

    from .projection import (  # noqa
        grow_streaming_item,

        TimelineProjectionError,
        UnknownProjectionItemError,
        StaleProjectionRevisionError,

        TimelineProjection,
    )

    from .state import (  # noqa
        TimelineState,
    )

    from .timeline import (  # noqa
        TimelineSubscriptionClosedError,
        TimelineSubscription,

        TimelineAttachment,

        Timeline,
    )

    from .translate import (  # noqa
        timeline_item_id_for_message,
        translate_message,

        AnchoredTimelineItem,
        translate_anchored_chat,
        translate_chat,
    )

    ##

    from . import inject  # noqa
    from . import injection  # noqa
