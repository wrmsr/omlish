# ruff: noqa: UP006 UP007
import datetime
import typing as ta

from omlish.lite.typing import Func0

from .tags import DeployTime


DEPLOY_TAG_DATETIME_FMT = '%Y%m%dT%H%M%SZ'


DeployManagerUtcClock = ta.NewType('DeployManagerUtcClock', Func0[datetime.datetime])


class DeployManager:
    def __init__(
            self,
            *,

            utc_clock: ta.Optional[DeployManagerUtcClock] = None,
    ):
        super().__init__()

        self._utc_clock = utc_clock

    def _utc_now(self) -> datetime.datetime:
        if self._utc_clock is not None:
            return self._utc_clock()  # noqa
        else:
            return datetime.datetime.now(tz=datetime.timezone.utc)  # noqa

    def make_deploy_time(self) -> DeployTime:
        return DeployTime(self._utc_now().strftime(DEPLOY_TAG_DATETIME_FMT))
