# ruff: noqa: UP007
import typing as ta

from . import protocol as pt


ClientRequestT = ta.TypeVar('ClientRequestT', bound='ClientRequest')
ClientResultT = ta.TypeVar('ClientResultT', bound='ClientResult')

ServerRequestT = ta.TypeVar('ServerRequestT', bound='ServerRequest')
ServerResultT = ta.TypeVar('ServerResultT', bound='ServerResult')


##
# FIXME: codegen lol


ClientRequest: ta.TypeAlias = ta.Union[
    pt.InitializeRequest,
    pt.PingRequest,
    pt.ListResourcesRequest,
    pt.ListResourceTemplatesRequest,
    pt.ReadResourceRequest,
    pt.SubscribeRequest,
    pt.UnsubscribeRequest,
    pt.ListPromptsRequest,
    pt.GetPromptRequest,
    pt.ListToolsRequest,
    pt.CallToolRequest,
    pt.SetLevelRequest,
    pt.CompleteRequest,
]

ClientResult: ta.TypeAlias = ta.Union[
    pt.Result,
    pt.CreateMessageResult,
    pt.ListRootsResult,
    pt.ElicitResult,
]

ClientNotification: ta.TypeAlias = ta.Union[
    pt.CancelledNotification,
    pt.InitializedNotification,
    pt.ProgressNotification,
    pt.RootsListChangedNotification,
]

#

ServerRequest: ta.TypeAlias = ta.Union[
    pt.PingRequest,
    pt.CreateMessageRequest,
    pt.ListRootsRequest,
    pt.ElicitRequest,
]

ServerResult: ta.TypeAlias = ta.Union[
    pt.Result,
    pt.InitializeResult,
    pt.ListResourcesResult,
    pt.ListResourceTemplatesResult,
    pt.ReadResourceResult,
    pt.ListPromptsResult,
    pt.GetPromptResult,
    pt.ListToolsResult,
    pt.CallToolResult,
    pt.CompleteResult,
]

ServerNotification: ta.TypeAlias = ta.Union[
    pt.CancelledNotification,
    pt.ProgressNotification,
    pt.ResourceListChangedNotification,
    pt.ResourceUpdatedNotification,
    pt.PromptListChangedNotification,
    pt.ToolListChangedNotification,
    pt.LoggingMessageNotification,
]


##


Message: ta.TypeAlias = ta.Union[
    ClientRequest,
    ClientResult,
    ClientNotification,

    ServerRequest,
    ServerResult,
    ServerNotification,
]
