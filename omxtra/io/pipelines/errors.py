# @omlish-lite


##


class ChannelPipelineError(Exception):
    pass


class IncompleteDecodingChannelPipelineError(ChannelPipelineError):
    pass


class FlowControlValidationChannelPipelineError(ChannelPipelineError):
    pass
