from omlish import inject as inj
from omlish import lang


with lang.auto_proxy_import(globals()):
    from ...drivers.storage import manager as _storage_manager
    from ...events import injection as _events_injection
    from ...events import manager as _events_manager
    from ...events import types as _events_types
    from . import history as _history
    from . import injection as _injection
    from . import manager as _manager
    from . import timeline as _timeline


##


def bind_timeline() -> inj.Elements:
    """
    Binds one `Timeline` (manager + state + composite history + subscription fan-out) into the enclosing - typically
    per-driver - scope, wired to the scope's event bus. Lego-style: drivers know nothing of timelines; attach this
    element set (or don't, or wire several managers) freely.

    The manager and timeline are both bus emitters *and* bus subscribers; their callback registrations resolve them
    lazily (`AsyncLate`) to break the otherwise-cyclic EventsManager <- callbacks <- manager <- EventsManager
    dependency.
    """

    els: list[inj.Elemental] = []

    #

    def _provide_timeline_manager(events: _events_manager.EventsManager) -> _manager.TimelineManager:
        return _manager.TimelineManager(events=events)

    def _provide_manager_callback(
            late_m: inj.AsyncLate[_manager.TimelineManager],
    ) -> _events_types.EventCallback:
        async def inner(event: _events_types.Event) -> None:
            await (await late_m()).handle_event(event)

        return _events_types.EventCallback(inner)

    els.extend([
        inj.bind(_provide_timeline_manager, singleton=True),
        inj.bind_async_late(_manager.TimelineManager),

        _events_injection.event_callbacks().bind_item(to_fn=_provide_manager_callback, singleton=True),
    ])

    #

    def _provide_timeline_history(
            storage: _storage_manager.DriverStorageManager,
            manager: _manager.TimelineManager,
    ) -> _history.TimelineHistory:
        return _history.CompositeTimelineHistory(
            storage=storage,
            state=manager.state,
        )

    els.append(inj.bind(_provide_timeline_history, singleton=True))

    #

    els.append(_injection.timeline_item_presenters().bind_items_provider(singleton=True))

    #

    def _provide_timeline_callback(
            late_t: inj.AsyncLate[_timeline.Timeline],
    ) -> _events_types.EventCallback:
        async def inner(event: _events_types.Event) -> None:
            await (await late_t()).handle_event(event)

        return _events_types.EventCallback(inner)

    els.extend([
        inj.bind(_timeline.Timeline, singleton=True),
        inj.bind_async_late(_timeline.Timeline),

        _events_injection.event_callbacks().bind_item(to_fn=_provide_timeline_callback, singleton=True),
    ])

    #

    return inj.as_elements(*els)
