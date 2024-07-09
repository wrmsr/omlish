import logging
import pytest

from .. import triotp2 as t2


class RecordingHandler(logging.Handler):
    def __init__(self, level: int = int) -> None:
        super().__init__(level)
        self.records: list[logging.LogRecord] = []

    def emit(self, record: logging.LogRecord) -> None:
        self.records.append(record)

    @property
    def has_errors(self) -> bool:
        return any(r.levelno >= logging.ERROR for r in self.records)


@pytest.fixture
def log_handler(monkeypatch):
    handler = RecordingHandler(logging.DEBUG)
    monkeypatch.setattr(t2._RetryLogger.logger, 'handlers', [handler])  # noqa
    yield handler


@pytest.fixture
def mailbox_env():
    t2.init_mailboxes()
