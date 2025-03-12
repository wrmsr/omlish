"""
https://github.com/wrmsr/bane/tree/master/x/storage
"""
import abc
import contextlib
import dataclasses as dc
import datetime
import uuid

import sqlalchemy as sa

from .... import lang


##


@dc.dataclass(frozen=True)
class Blob:
    key: bytes
    value: bytes

    created_at: datetime.datetime
    updated_at: datetime.datetime


class BlobStorage(abc.ABC):
    @abc.abstractmethod
    def get(self, key: bytes) -> Blob | None:
        raise NotImplementedError

    @abc.abstractmethod
    def put(self, key: bytes, value: bytes) -> None:
        raise NotImplementedError


class NopBlobStorage(BlobStorage):
    def get(self, key: bytes) -> Blob | None:
        raise TypeError

    def put(self, key: bytes, value: bytes) -> None:
        raise TypeError


class DictBlobStorage(BlobStorage):
    def __init__(self) -> None:
        super().__init__()
        self._dct: dict[bytes, Blob] = {}

    def get(self, key: bytes) -> Blob | None:
        return self._dct.get(key)

    def put(self, key: bytes, value: bytes) -> None:
        try:
            blob = self._dct[key]
        except KeyError:
            self._dct[key] = Blob(
                key=key,
                value=value,
                created_at=lang.utcnow(),
                updated_at=lang.utcnow(),
            )
        else:
            self._dct[key] = dc.replace(
                blob,
                value=value,
                updated_at=lang.utcnow(),
            )


##


@dc.dataclass(frozen=True)
class JournalEntry:
    id: uuid.UUID

    key: bytes
    value: bytes

    created_at: datetime.datetime


class Journal(abc.ABC):
    @abc.abstractmethod
    def write(self, key: bytes, value: bytes) -> None:
        raise NotImplementedError


class NopJournal(Journal):
    def write(self, key: bytes, value: bytes) -> None:
        pass


class ListJournal(Journal):
    def __init__(self) -> None:
        super().__init__()
        self._lst: list[JournalEntry] = []

    def write(self, key: bytes, value: bytes) -> None:
        self._lst.append(JournalEntry(
            id=uuid.uuid4(),
            key=key,
            value=value,
            created_at=lang.utcnow(),
        ))


##


class DbBlobStorage(BlobStorage):
    def __init__(
            self,
            engine: sa.Engine,
            table_name: str,
    ) -> None:
        super().__init__()

        self._metadata = sa.MetaData()
        self._table = sa.Table(
            table_name,
            self._metadata,

            sa.Column('key', sa.String(50), primary_key=True),
            sa.Column('value', sa.String(50), primary_key=True),

            sa.Column('created_at', sa.TIMESTAMP(timezone=True)),
            sa.Column('updated_at', sa.TIMESTAMP(timezone=True)),
        )

    def get(self, key: bytes) -> Blob | None:
        raise NotImplementedError

    def put(self, key: bytes, value: bytes) -> None:
        raise NotImplementedError


def test_db_blob_storage():
    with contextlib.ExitStack() as es:
        engine = sa.create_engine(f'sqlite://', echo=True)
        es.enter_context(lang.defer(engine.dispose))

        bs = DbBlobStorage(
            engine,
            '_test_blob_storage',
        )

        with engine.begin() as conn:
            bs._metadata.create_all(bind=conn)  # noqa

            conn.execute(
                bs._table.insert(), [  # noqa
                    {
                        'key': 'some key',
                        'value': 'some value',
                        'created_at': lang.utcnow(),
                        'updated_at': lang.utcnow(),
                    },
                ],
            )
