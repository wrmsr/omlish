The core service abstraction. In general, Services are intended to encapsulate non-trivial, resourceful, effectful
operations, which are likely to have various implementations, each having their own specific capabilities in addition
to their common interface, and where wrapping, adapting, and transforming them in a uniform manner is desirable.

For example:
 - A ChatService is passed a Request with a Chat value and returns a Response with an AiChat value.
 - A ChatChoicesService is passed a Request with a Chat and returns a Response with a list of AiChoices.
 - A ChatChoicesServiceChatService is a simple adapter taking a ChatChoicesService which it will invoke with its given
   Request, expect a single AiChoice value in that Response, and return that single AiChat as its Response - thus acting
   as a ChatService.
   - Thus, all chat backends that return choices can be adapted to code expecting a single chat as output.
 - A ChatStreamService is passed a Request with a Chat value and returns a Response with a value from which AiDeltas
   may be streamed.
 - A ChatChoicesStreamService is passed a Request with a Chat value and returns a Response with a value from which
   AiChoicesDeltas may be streamed.
 - A ChatChoicesStreamServiceChatChoicesService is an adapter taking a ChatChoicesStreamService and aggregating the
   AiChoicesDeltas into joined, non-delta AiChoices.
   - This may then be wrapped in a ChatChoicesServiceChatService to act as a ChatService.
   - In practice however there are usually dedicated streaming and non-streaming implementations if possible as
     non-streaming will usually have less overhead.
 - An OpenaiChatChoicesService can act as a ChatChoicesService, and will accept all generic ChatOptions, in addition to
   any OpenaiChatOptions inapplicable to any other backend. It may also produce all generic ChatOutputs, in addition to
   OpenaiChatOutputs that will not be produced by other backends.
 - Beyond chat, a VectorSearchService is passed a Request with a VectorSearch value and returns a Response with a
   VectorHits value.
 - A RetryService wraps any other Service and will attempt to re-invoke it on failure.
 - A FirstInWinsService wraps any number of other Services and will return the first non-error Response it receives.

The service abstraction consists of 3 interrelated generic types:
 - Request, an immutable final generic class containing a single value and any number of options.
 - Response, an immutable final generic class containing a single value and any number of outputs.
 - Service, a generic protocol consisting of a single async method `invoke`, taking a request and returning a response.

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
 - These types are *not* intended to form a deep type hierarchy:
   - A RemoteChatOption is *not* intended to inherit from a ChatOption: a ChatOption (be it a base class or union alias)
     represents an option that *any* ChatService can accept, whereas a RemoteChatOption represents an option that *only*
     applies to a RemoteChatService.
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
   - A RemoteChatResponse *is a* ChatResponse even though it may contain additional output variants not produced by
     every ChatService.
   - Code that calls a ChatService and is given a ChatResponse must be prepared to handle (usually by simply ignoring)
     outputs not necessarily produced by a base ChatService.

Finally, in addition to a value and either options or outputs, a Request and Response each also contain a collection of
metadata. Very much unlike the Options and Outputs, the elements of these collections are simply of the types
`RequestMetadata | CommonMetadata` and `ResponseMetadata | CommonMetadata`, and are not otherwise parameterized. These
are intended for looser inputs and outputs: a generic unique id, timestamps, metrics, etc., and in general should
neither affect the behavior of services nor be depended upon by callers.

Below is a representative illustration of these types and their relationships. Note how:
 - There is no subclassing of Request, Response, or Service - just type aliasing.
 - There is no deep, shared subclassing of Option or Output.
 - The type args passed to Request and Response are unions of all the Option and Output subtypes they may contain.
   - These unions are kept in pluralized type aliases for convenience.
 - There is no base ChatOption or ChatOutput class - were there, it would not be included in the base classes of any
   local or remote only option or output.
 - The local and remote sections take different but equivalent approaches:
   - There are no base LocalChatOption or LocalChatOutput classes, but there *are* base RemoteChatOption and
     RemoteChatOutput classes.
   - Without any common base classes (besides the lowest level Output and Option classes), the local section treats them
     as each distinct and bespoke, and the pluralized LocalChatOptions and LocalChatOutputs type aliases aggregate them
     by explicitly listing them.
   - With the common RemoteChatOption and RemoteChatOutput base classes, the remote section treats them as a related
     family that any 'RemoteChat'-like service should accept and produce.

```python
# Common chat

class MaxTokens(Option, tv.UniqueScalarTypedValue[int]): pass
class Temperature(Option, tv.UniqueScalarTypedValue[float]): pass

ChatOptions: ta.TypeAlias = MaxTokens | Temperature
ChatRequest: ta.TypeAlias = Request[Chat, ChatOptions]

class TokenUsage(Output, tv.UniqueScalarTypedValue[int]): pass
class ElapsedTime(Output, tv.UniqueScalarTypedValue[float]): pass

ChatOutputs: ta.TypeAlias = TokenUsage | ElapsedTime
ChatResponse: ta.TypeAlias = Response[Message, ChatOutputs]

ChatService: ta.TypeAlias = Service[ChatRequest, ChatResponse]

# Local chat

class ModelPath(Option, tv.ScalarTypedValue[str]): pass

LocalChatOptions: ta.TypeAlias = ChatOptions | ModelPath
LocalChatRequest: ta.TypeAlias = Request[Chat, LocalChatOptions]

class LogPath(Output, tv.ScalarTypedValue[str]): pass

LocalChatOutputs: ta.TypeAlias = ChatOutputs | LogPath
LocalChatResponse: ta.TypeAlias = Response[Message, LocalChatOutputs]

LocalChatService: ta.TypeAlias = Service[LocalChatRequest, LocalChatResponse]

# Remote chat

class RemoteChatOption(Option, lang.Abstract): pass
class ApiKey(RemoteChatOption, tv.ScalarTypedValue[str]): pass

RemoteChatOptions: ta.TypeAlias = ChatOptions | RemoteChatOption
RemoteChatRequest: ta.TypeAlias = Request[Chat, RemoteChatOptions]

class RemoteChatOutput(Output, lang.Abstract): pass
class BilledCostInUsd(RemoteChatOutput, tv.UniqueScalarTypedValue[float]): pass

RemoteChatOutputs: ta.TypeAlias = ChatOutputs | RemoteChatOutput
RemoteChatResponse: ta.TypeAlias = Response[Message, RemoteChatOutputs]

RemoteChatService: ta.TypeAlias = Service[RemoteChatRequest, RemoteChatResponse]
```

