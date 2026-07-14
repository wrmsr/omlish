# omcore.orm

A small async ORM over dataclass-mapped models: explicit mappers, unit-of-work sessions, store-abstracted persistence
(in-memory and SQL via the in-house `omcore.sql` api). It is deliberately modest — closer to a typed row-mapper with
sessions than to SQLAlchemy — and it evolves with its consumers' needs.

This README covers usage and, importantly, the **current concurrency semantics and sharp edges**, which are easy to
trip over and not visible from the API surface.


## Models and mappers

Models are ordinary (mutable) dataclasses; `install_class_field_attrs='instance'` makes class-level field references
(`OrmMessage.chat`) available for backref declarations:

```python
@dc.dataclass(kw_only=True)
@dc.extra_class_params(install_class_field_attrs='instance')
class OrmChat:
    id: orm.Key[uuid.UUID] = dc.field(default_factory=orm.key_wrapping(uuid.uuid7))

    created_at: datetime.datetime = orm.auto_value[datetime.datetime]()
    updated_at: datetime.datetime = orm.auto_value[datetime.datetime]()

    name: str | None = None
    num_messages: int = 0

    messages: ta.ClassVar[orm.Backref[OrmMessage]] = orm.backref(lambda: OrmMessage.chat)  # type: ignore[misc]


@dc.dataclass(kw_only=True)
@dc.extra_class_params(install_class_field_attrs='instance')
class OrmMessage:
    id: orm.Key[uuid.UUID] = dc.field(default_factory=orm.key_wrapping(uuid.uuid7))

    chat: orm.Ref[OrmChat, uuid.UUID]
    seq: int

    message: Message  # a rich domain value - see the field codec below
```

Key flavors: `orm.Key[K]` with `orm.key(value)` / `orm.key_wrapping(factory)` for natural/uuid keys, or
`orm.auto_key[int]` for store-assigned auto-increment. `orm.Ref[T, K]` fields hold references (`orm.ref(obj)` to
construct); awaiting the instance attribute resolves it (`await orm_msg.chat()`), and `orm.Backref` declares the
reverse (`await orm_chat.messages()`).

Mappers are built explicitly — usually `dataclass_mapper`, with per-field options and indexes — and collected into a
registry:

```python
def storage_mappers() -> ta.Sequence[orm.Mapper]:
    return [
        orm.dataclass_mapper(
            OrmChat,
            store_name='chats',
            field_options=dict(
                created_at=[orm.CreatedAt()],
                updated_at=[orm.UpdatedAt()],
            ),
            indexes=['name'],
        ),

        orm.dataclass_mapper(
            OrmMessage,
            store_name='messages',
            field_options=dict(
                # Rich domain values persist via codecs - here marshal -> json -> string column:
                message=[
                    orm.FieldCodec(orm.CompositeCodec(
                        orm.MarshalCodec(),
                        orm.JsonCodec(),
                    )),
                    orm.FieldSqlType(sql.td.String()),
                ],
            ),
            indexes=[
                orm.index(['chat', 'seq'], options=[orm.UniqueIndexOption(), orm.SortedIndexOption()]),
            ],
        ),
    ]


registry = orm.registry(*storage_mappers())
```

`CreatedAt()`/`UpdatedAt()` field options drive the `auto_value` timestamp fields; `Ref` fields get `_id`-suffixed
store names by default.


## Sessions and the module-level api

A `Session` is a unit of work over `(registry, store)`; activating it (which `orm.session(...)` does) binds it to a
contextvar that the module-level api functions use:

```python
async with orm.session(registry, store) as sess:  # noqa
    chat = await orm.add_one(OrmChat())

    await orm.add(OrmMessage(chat=orm.ref(chat), seq=1, message=msg))
    chat.num_messages += 1          # plain attribute mutation - flushed on session close

    found = await orm.get(OrmChat, chat.id)
```

The api: `add` / `add_one`, `get(cls, key)`, `delete`, `flush`, `refresh` / `refresh_one`, `abort` (rollback), and
queries:

```python
rows = await orm.query(orm.Query(
    OrmMessage,
    orm.Where(
        orm.WhereItem.of('chat', '=', orm.ref(chat)),
        orm.WhereItem.of('seq', '>', 5),
    ),
    order_by=[orm.OrderByItem('seq', 'desc')],
    limit=10,
))

one = await orm.query_one(OrmChat, name='main')   # kwarg shorthand for equality wheres
```

Changes (adds, deletes, attribute mutations of session-loaded objects) flush at session close — the session is
transactional: it all lands or none of it does.


## Stores

- **`InMemoryStore`** — dict/snapshot-backed, with index support and deliberately simple transactionality (a
  reader-writer discipline that is *safe* but blunt: conflicting work may only fail at commit). Two things to know:
  - **Tables key on `Mapper` identity.** Two registries (e.g. two injectors in one process) each build their own
    mapper instances; pointing them at one shared `InMemoryStore` collides on store names. An in-memory store is
    effectively single-registry — for cross-"session" persistence scenarios, use the SQL store on a temp file.
  - It is the right default for tests within one wiring.
- **`SqlStore`** — over `omcore.sql.api` async databases (commonly sqlite via a single-threaded executor). Creates
  schema on demand; tolerates pre-existing tables.


## Concurrency semantics and sharp edges (current state)

These reflect the implementation as of this writing; they are the part most worth knowing.

1. **One session = one connection holding one transaction for its whole life.** The session's store context opens a
   connection and (by default) issues a plain `BEGIN`, committing at `finish`/close. Everything inside — including
   any `await`s your code does between orm calls — happens under that open transaction.

2. **Plain `BEGIN` is deferred — and read-then-write sessions upgrade.** A session that `SELECT`s and then
   `INSERT`s/`UPDATE`s (the very common "get-or-create" shape) upgrades its transaction from read to write at the
   first write. Under sqlite (WAL), **if any other connection committed a write between the session's first read
   and its upgrade, the upgrade fails immediately with `database is locked`** (`SQLITE_BUSY_SNAPSHOT`) — the busy
   timeout does *not* apply to snapshot-upgrade conflicts, so this is not a slow-contention symptom but an
   interleaving one. Concretely: two concurrent get-or-create sessions against one sqlite file can fail even at
   trivial load.

   Until write-bearing sessions take their write lock up front (`BEGIN IMMEDIATE`, or upgrade-with-retry — a known
   future direction), the working guidance is: **serialize write-bearing sessions against each other** at the
   application level (e.g. sequence startup writes before opening concurrent readers; funnel writes through one
   actor). Pure-read sessions are safe alongside a writer under WAL.

3. **Connections may be per-operation at the `sql.api` layer** (`DbapiDb` connects per query context) but the orm
   session pins one for its duration — so "how many connections is this code holding" is a per-session question,
   and N concurrent sessions are N connections.

4. **Auto-key inserts round-trip** (`insert ... returning id`) inside the session's transaction like any other
   write — they participate in the upgrade hazard above.

5. The in-memory store's transactionality is *optimistic-ish and blunt*: it is safe, but late conflict surfacing is
   by design for now. Don't infer SQL-store semantics from it or vice versa.

When in doubt, the e2e patterns in `ommlds/minichain/drivers/testing.py` and the timeline test suites show the
known-good shapes (including real-sqlite multi-session testing on `tmp_path`).
