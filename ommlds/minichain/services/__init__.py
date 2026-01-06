# ruff: noqa: I001
"""
The core service abstraction, consisting of 3 interrelated generic types:
 - Request, an immutable final generic class containing a single value and any number of options.
 - Response, an immutable final generic class containing a single value and any number of outputs.
 - Service, a generic protocol consisting of a single method `invoke`, taking a request and returning a response.

There are 2 related abstract base classes in the parent package:
 - Option, a non-generic abstract class representing a service option.
 - Output, a non-generic abstract class representing a service output.

The purpose of this arrangement is to provide the following:
 - There is only one method - `Service.invoke` - to deal with.
 - There is no base `Service` class - service types are distinguished only by the requests they accept and responses
   they return.
 - It facilitates a clear, introspectable, generally type-safe means for handling 'less-specific' and 'more-specific'
   service types.
 - It facilitates generic wrapper and transformation machinery.

The variance of the type parameters of the 3 classes is central:
 - `Request[V_co, OptionT_co]`
 - `Response[V_co, OutputT_contra]`
 - `Service[RequestT_contra, ResponseT_co]`

And to understand this, it's important to understand how Option and Output subtypes are intended to be arranged:
 - These types are *not* intended to form a mutli-level type hierarchy: a RemoteChatOption is *not* intended to inherit
   from a ChatOption: a ChatOption (beit a base class or union alias) represents an option that *any* ChatService can
   accept, whereas a RemoteChatOption represents an option that *only* applies to a RemoteChatService.
   - If RemoteChatOption inherited from a base ChatOption, then it would have to apply to *all* ChatService
     implementations.
   - For example: were ApiKey to inherit from ChatOption, then it would have to apply to all ChatServices, including
     LocalChatService, which has no concept of an api key.
 - Similarly, a RemoteChatOutput is *not* intended to inherit from a ChatOutput: a ChatOutput represents an output that
   *any* ChatService can produce, whereas a RemoteChatOutput represents an output that *only* applies to a
   RemoteChatService.
 - These 2 types are intended to form flat, disjoint, unrelated families of subtypes, and Request and Response are
   intended to be parameterized by the unions of all such families they may contain.
 - Because of this, one's visual intuition regarding types and subtypes may be reversed: `int` is effectively a subtype
   of `int | str` despite `int` being a visually shorter, less complex type.
   - `int` is a *MORE SPECIFIC* / *STRICT SUBSET* subtype of `int | str`, the *LESS SPECIFIC* / *STRICT SUPERSET*
     supertype.

Regarding type variance:
 - Service has the classic setup of contravariant input and covariant output:
  - A RemoteChatService *is a* ChatService.
  - A RemoteChatService may accept less specific requests than a ChatService.
  - A RemoteChatService may return more specific responses than a ChatService.
 - Request is covariant on its options:
  - Recall, a RemoteChatOption *is not a* ChatOption.
  - A ChatRequest *is a* RemoteChatRequest as it will not contain options RemoteChatService cannot accept.
 - Response is contravariant on its outputs:
  - Recall, a RemoteChatOutput *is not a* ChatOutput.
  - A RemoteChatResponse *is a* ChatResponse even though it may contain additional output variants not produced by every
    ChatService.
  - Code that calls a ChatService and is given a ChatResponse must be prepared to handle (usually by simply ignoring)
    outputs not necessarily produced by a base ChatService.

Consider the following representative illustration:

```
# Common chat

class MaxTokens(Option, tv.UniqueScalarTypedValue[int]): pass
class Temperature(Option, tv.UniqueScalarTypedValue[float]): pass

ChatOption: ta.TypeAlias = MaxTokens | Temperature
ChatRequest: ta.TypeAlias = Request[Chat, ChatOption]

class TokenUsage(Output, tv.UniqueScalarTypedValue[int]): pass
class ElapsedTime(Output, tv.UniqueScalarTypedValue[float]): pass

ChatOutput: ta.TypeAlias = TokenUsage | ElapsedTime
ChatResponse: ta.TypeAlias = Response[Message, ChatOutput]

ChatService: ta.TypeAlias = Service[ChatRequest, ChatResponse]

# Local chat

class ModelPath(Option, tv.ScalarTypedValue[str]): pass

LocalChatOption: ta.TypeAlias = ChatOption | ModelPath
LocalChatRequest: ta.TypeAlias = Request[Chat, LocalChatOption]

class LogPath(Output, tv.ScalarTypedValue[str]): pass

LocalChatOutputs: ta.TypeAlias = ChatOutput | LogPath
LocalChatResponse: ta.TypeAlias = Response[Message, LocalChatOutputs]

LocalChatService: ta.TypeAlias = Service[LocalChatRequest, LocalChatResponse]

# Remote chat

class ApiKey(Option, tv.ScalarTypedValue[str]): pass

RemoteChatOptions: ta.TypeAlias = ChatOption | ApiKey
RemoteChatRequest: ta.TypeAlias = Request[Chat, RemoteChatOptions]

class BilledCostInUsd(Output, tv.UniqueScalarTypedValue[float]): pass

RemoteChatOutput: ta.TypeAlias = ChatOutput | BilledCostInUsd
RemoteChatResponse: ta.TypeAlias = Response[Message, RemoteChatOutput]

RemoteChatService: ta.TypeAlias = Service[RemoteChatRequest, RemoteChatResponse]
```
"""


from .facades import (  # noqa
    ServiceFacade,

    facade,
)

from .requests import (  # noqa
    RequestMetadata,
    RequestMetadatas,

    Request,
)

from .responses import (  # noqa
    ResponseMetadata,
    ResponseMetadatas,

    Response,
)

from .services import (  # noqa
    Service,
)


##


from omlish import marshal as _msh

_msh.register_global_module_import('._marshal', __package__)
