# HTTP chat backends

The anatomy of an external chat backend, and the conventions every one of them follows. This covers the HTTP
backends — openai (chat-completions *and* responses), groq, cerebras, anthropic, google (gemini), ollama. In-proc
backends (llamacpp, tinygrad, mlx, ...) are a different animal and not described here.

The guiding idea is the compiler framing: **one service driver per wire-dialect family, with per-vendor lowering
only where the wire genuinely differs.** Differences that deserve to exist — anthropic's typed event family,
google's parts model, ollama's JSONL, the openai-compat `channel`/`reasoning` extensions — are celebrated. The 80%
that is the same (config consumption, request assembly, HTTP, envelope decode, translation, status/error/event
handling) is shared.


## The two layers

Every backend is split across two packages:

1. **`ommlds/backends/<vendor>/`** — the minichain-agnostic **vendor IR**. Frozen, `kw_only`, marshal-first
   dataclasses that mirror the vendor's wire format 1:1, with a doc-URL header on each module. No minichain imports.
   Polymorphic unions (content parts, sse events, input/output items) use marshal polymorphism, registered in a
   `_marshal.py` and wired through the package `__init__.py`. Wire-level *dialect extensions* (fields the base
   vendor never sends but a compatible vendor does — e.g. `ChatCompletionChunkChoiceDelta.channel`) live here as
   marked optional fields.

2. **`ommlds/minichain/backends/<vendor>/`** — the **services and translation**. The `Service` classes plus the
   passes that translate between the mc chat IR (`Chat`/`Message`/`AiChoice`/`AiDelta`) and the vendor IR.

The mc layer translates *to* the vendor IR for requests and *from* it for responses; it never re-defines the wire
format.


## Standard module layout (mc layer)

| module | holds |
| --- | --- |
| `names.py` | the `ModelNameCollection` (aliases, default) and the `BackendStringsManifest` |
| `protocol.py` | the translation passes (mc ↔ vendor IR) and any streaming delta translator |
| `chat.py` | the shared service base + the non-stream `...ChatChoicesService` |
| `stream.py` | the streaming `...ChatChoicesStreamService` |
| `tests/` | offline translation tests + `@online` smokes |

`chat.py` holding the shared base (config consumption, header/url building, request assembly) and `stream.py`
importing it is the standard split — it keeps the base next to the non-stream service and avoids a circular import.


## Translation-fn vocabulary

Name the passes consistently so a reader can move between backends:

- `build_<pfx>_request_*` / `build_<pfx>_request_content` — mc → vendor IR for requests (`<pfx>` is the vendor short
  prefix: `oai`, `ant`, `ol`, `g`, ...). e.g. `build_oai_request_msgs`, `build_ant_request_messages`,
  `build_g_request_content`, `build_ol_request_tool`.
- `build_mc_choices_response(...)` — vendor response IR → `ChatChoicesResponse` (non-stream).
- `build_mc_ai_deltas(...)` / `build_mc_ai_choices_deltas(...)` — vendor stream chunk/event → mc `AiDelta`s.
- A `...SseDeltaTranslator` / state-machine class when the stream carries cross-event state (anthropic's
  block/message envelope, the responses event family). It returns a typed `Result(deltas, done)` and (if it has
  ordering invariants) validates them in `translate`/`finish` — never an inline state machine in `invoke`.

Reassembly of streamed deltas into canonical messages is **not** the backend's job — emit `AiDelta`s (incl.
`PartialToolUseAiDelta(index=...)` for incremental tool args) and let `AiDeltaJoiner` group and join them.


## The service bar (what every backend must do)

- **Options: consume or explicitly reject — never silently drop.** Pop the options you support
  (`Temperature`, `MaxTokens`, `Tool`, ...) via `tv.consume`; let `tv.consume`'s unconsumed-check raise on anything
  unrecognized. Filter out the transport options that aren't the backend's to read
  (`ChatChoicesStreamOption`, `StreamOption`, `ResourcesOption`) before consuming.
- **Status checking.** Non-200 raises `HttpStreamResponseError` (the streaming builder does this for you; non-stream
  services check `http_response.status` explicitly). Don't let a non-200 body fall through to json/unmarshal.
- **`on_event` emission.** Accept `on_event: EventCallback | None` and emit `ExternalServiceRequestEvent` +
  `ExternalServiceResponseEvent` (non-stream) / `ExternalServiceStreamResponseDataEvent` (per stream datum).
- **Config ctor.** `__init__(self, *configs: ApiKey | ModelName, http_client=None, on_event=None)` — the
  annotation must be the *specific* consumable union (not bare `Config`); the backend-spec resolver introspects it
  to type-validate per-backend configs.
- **Streaming rides the shared builder.** Use `BytesHttpStreamResponseBuilder` with a
  `Simple{Sse,Lines}HttpStreamResponseHandler` (see `minichain/http/stream.py`) — it owns status checking, resource
  management, framing, and the read loop. Don't hand-roll the byte loop.


## The openai-compat dialect (add a vendor in ~20 lines)

OpenAI's chat-completions wire format is a de-facto dialect spoken by many vendors (groq, cerebras, ollama's
`/v1/chat/completions`, vllm, llama.cpp's server, ...). `minichain/backends/openai/compat.py` is the *one*
implementation of its service machinery; openai's own services are the reference instance. A compatible vendor is a
pair of thin subclasses setting the knobs that legitimately differ:

```python
class GroqChatChoicesServiceBase(OpenaiCompatChatChoicesServiceBase):
    URL = 'https://api.groq.com/openai/v1/chat/completions'
    API_KEY_ENV = 'GROQ_API_KEY'
    EXTRA_HEADERS = REQUIRED_HTTP_HEADERS
    MODEL_NAMES = names.MODEL_NAMES
    DEFAULT_MODEL_NAME = ModelName(check.not_none(names.MODEL_NAMES.default))

class GroqChatChoicesService(GroqChatChoicesServiceBase, OpenaiCompatChatChoicesService): ...
# stream.py: class GroqChatChoicesStreamService(GroqChatChoicesServiceBase, OpenaiCompatChatChoicesStreamService): ...
```

Wire-level dialect quirks go in two places: marked optional fields on the openai vendor IR (the `channel` /
`reasoning` extensions), and translation-level handling in `openai/protocol.py` (e.g. skipping the gpt-oss
analysis/commentary reasoning channels). Don't clone the protocol — extend the reference one.


## A genuinely-different backend (anthropic, google, ollama-native, openai-responses)

When the wire format is *not* the openai-compat dialect, write a real backend: a vendor IR package, a `protocol.py`
with `build_<pfx>_*` / `build_mc_*` passes, and `chat.py`/`stream.py` on the conventions above. It still shares the
HTTP/SSE transport (the builder) and the service skeleton (config consumption, on_event, status handling, the
options bar) — only the wire format and its translation are bespoke. The responses backend is the in-between case:
its own wire format, but it reuses the openai-compat *config/auth/header* base (`OpenaiCompatChatChoicesServiceBase`)
without inheriting the chat-completions request/envelope drivers — the boundary between shared plumbing and shared
wire.


## Tests

Two tiers, both expected:

- **Offline** (`test_proto.py` / `test_compat.py` / `test_responses.py` / `test_stream_proto.py`): translation both
  ways, option honoring, and — the load-bearing one — a realistic chunk/event sequence fed through the translator
  and the **real `AiDeltaJoiner`**, asserting the joined `AiMessage`/`ToolUseMessage` output. Captured wire fixtures
  (e.g. anthropic's `story.txt`) are gold. Marshal round-trips for the vendor IR live under
  `ommlds/backends/<vendor>/.../tests/`.
- **Online** (`@pytest.mark.online`): live smokes that skip without an API key.


## See also

- `ommlds/minichain/http/stream.py` — the shared streaming transport (`BytesHttpStreamResponseBuilder`, the
  handler layers, `HttpStreamResponseError`).
- `ommlds/minichain/services/README.md` — the `Service`/`Request`/`Response` abstraction these implement.

