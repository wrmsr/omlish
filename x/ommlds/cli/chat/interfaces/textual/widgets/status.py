from omdev.tui import textual as tx
from omcore.term.spinners import SPINNERS

from ..drivers.types import ChatDriverInterfaceState


##


class StatusBar(tx.InitAddClass, tx.Static):
    init_add_class = 'status-bar'

    def __init__(
            self,
            content: str,
    ) -> None:
        super().__init__()

        self._content = content

    def compose(self) -> tx.ComposeResult:
        yield tx.Static(self._content)


class DriverStateIndicator(tx.InitAddClass, tx.Static):
    init_add_class = 'driver-state-indicator'

    def __init__(self) -> None:
        super().__init__()

        self._spin_frames = SPINNERS['dots3']
        self._spin_frame = 0
        self._spin_timer: tx.Timer | None = None

    def on_mount(self) -> None:
        self._set_driver_state(ChatDriverInterfaceState.IDLE)

    def _update_spin(self) -> None:
        i = self._spin_frame + 1
        if i >= len(self._spin_frames):
            i = 0
        self._spin_frame = i
        self.update(tx.Text(self._spin_frames[i]))

    def _set_driver_state(self, state: ChatDriverInterfaceState) -> None:
        self._state = state

        if (st := self._spin_timer) is not None:
            st.stop()
        self._spin_timer = None
        self._spin_frame = -1

        if self._state == ChatDriverInterfaceState.ACTIVE:
            self._update_spin()
            self._spin_timer = self.set_interval(.1, self._update_spin)

        else:
            self.update(tx.Text(' '))

        self.set_class(self._state == ChatDriverInterfaceState.ACTIVE, 'active')
        self.set_class(self._state == ChatDriverInterfaceState.IDLE, 'idle')

    def set_driver_state(self, state: ChatDriverInterfaceState) -> None:
        if self._state is state:
            return

        self._set_driver_state(state)


class StatusContainer(tx.InitAddClass, tx.ComposeOnce, tx.Static):
    init_add_class = 'status-container'

    def __init__(self) -> None:
        super().__init__()

        self._driver_state_indicator = DriverStateIndicator()
        self._status_bar = StatusBar(' ')

    def set_driver_state(self, state: ChatDriverInterfaceState) -> None:
        self._driver_state_indicator.set_driver_state(state)

    def _compose_once(self) -> tx.ComposeResult:
        with tx.Horizontal(classes='status-horizontal'):
            yield self._driver_state_indicator
            yield self._status_bar
