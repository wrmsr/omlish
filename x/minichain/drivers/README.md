# Drivers

The headless agent: a `Driver` accepts `Action`s (currently: send user messages), runs the generation loop
(prepare -> LLM -> execute tools -> repeat until no tool uses), persists the result, and narrates everything as
events on the scope's bus. Frontends never talk to a driver beyond `do_action`/`start`/`stop`; everything they
display comes from events (via `facades/timelines`).

## Data flow, per `SendUserMessagesAction`

1. The user chat is transformed (`MessageUuid`/`CreatedAt` stamping - add-if-missing, so caller-stamped uuids like
   the facade's `input_uuid` survive) and `UserMessagesEvent` is emitted.
2. The prior chat is loaded from storage, the new user messages appended, and the `ChatPreparer` runs (system
   message providers, placeholder contents).
3. The `AiChatGenerator` stack generates, looping tools (see "The generator stack").
4. The user messages and the entire generated output (including tool use/result messages) are persisted via
   `DriverStorageManager.extend_chat` - **only at action end**, transactionally. A failed action persists nothing,
   its user message included.

Actions are serialized per driver (an internal lock); cancellation is currently a frontend concern (cancel the task
awaiting `do_action`).

## The generator stack

Composed in `ai/inject.py` via `wrapper_binder_helper`, outermost first:

    ToolExecuting( EventEmitting( ChatTransform( ChatChoicesStreamServiceStreamAiChatGenerator( service ) ) ) )

`ToolExecuting` loops: each inner call is one LLM segment; its tool uses are executed (through the executor stack,
below) and their results appended, then the loop re-invokes the inner generator with the extended chat.

## THE EVENT ORDERING CONTRACT

Because `EventEmitting` sits *inside* the tool loop, the bus sees, per action:

    UserMessagesEvent
    -- per LLM segment:
       AiStreamBeginEvent / AiStreamDeltaEvent* / AiStreamEndEvent   (per *message*, see below)
       AiMessagesEvent(streamed=True)        <- the joined canonical messages for the segment
       ToolUseEvent / ToolUseResultEvent     <- that segment's tool executions, between segments
    -- next segment...

Things downstream code relies on (the timelines manager most of all):

- **Streamy talks down, never up.** Stream-capable code must also be consumable non-streamily: after a successful
  stream, the joined `AiMessagesEvent(streamed=True)` always follows, carrying the same content as canonical
  messages. Non-stream-aware listeners ignore stream events (like any unknown event) and consume the joined one;
  stream-aware listeners must know to skip it (or, like the timeline manager, *use* it for reconciliation). In the
  non-streaming configuration the same event arrives with `streamed=False` and no stream events precede it.
- **`AiStreamBegin/EndEvent` demarcate per-*message* spans within a stream, not LLM segments.** A segment that
  streams prose then a tool call produces two Begin/End pairs (one per `MessageUuid`). Deltas between them carry
  the message uuid (stamped by `TypeSequentialMessageUuidAddingAiDeltaTransform`).
- **A successful stream's joined messages carry the same `MessageUuid`s as its deltas did** (the joiner confers
  them) - this is what makes stream->canonical identity work.
- **An exceptional stream end emits `AiStreamEndEvent(exception=...)`** (shielded), and no joined messages event
  follows; the action raises.
- **Tool events are emitted by the outermost executor wrapper** (`EventEmittingToolUseExecutor`), so
  `ToolUseResultEvent.tur` is the final, metadata-stamped result - byte-for-byte what gets persisted in the
  `ToolUseResultMessage`. (`ToolUseEvent.use` is the pre-stamp use, matching the persisted `ToolUseMessage.tu`.)

## The tool executor stack

Composed in `tools/inject.py`, outermost first:

    EventEmitting( MetadataAdding( ErrorHandling( ToolUseExecutorImpl ) ) )

`ErrorHandling` converts `ToolExecutionError`s (including permission denials) into ordinary results whose content
describes the failure - so today, denials/failures surface as COMPLETE results, not distinct event shapes.
`MetadataAdding` stamps `ToolUseUuid`/`CreatedAt`. `ToolUseExecutorImpl` binds contextual values (`cxl`) and
invokes the catalog entry. Note `ToolUseExecutorImpl` resolves its context providers eagerly at construction: with
tools enabled, a `ToolPermissionDecider` binding must exist even if no tool consults it (tests: see
`drivers/testing.py`'s allow-all + override pattern).

## Storage

`OrmChat` / `OrmMessage(chat, seq, message)` / `OrmDriver` over the in-house ORM; `OrmMessage` row keys **are** the
messages' `MessageUuid`s, and `seq` is 1-based and dense per chat. Paging (`get_latest_chat_page` /
`get_chat_page_before` / `get_chat_page_after`) returns seq-bearing `StoredMessage` rows. In-memory store by
default; sqlite (WAL) via `OrmConfig(file_path='....db')` - which is also how multi-session tests share state
(`orm.InMemoryStore` cannot be shared across injectors; its tables key on mapper identity).

## Testing

`drivers/testing.py` provides `bind_scripted_driver`: the complete driver wired to the programmable `scripted`
backend - the supported way to write offline end-to-end driver tests. See `drivers/tests/test_scripted.py` for the
basic pattern and `facades/timelines/tests/` for the full harness (timelines attached, lock-step gates, sqlite
multi-session).
