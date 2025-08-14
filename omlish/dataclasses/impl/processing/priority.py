import enum


##


class ProcessorPriority(enum.IntEnum):
    BOOTSTRAP = enum.auto()

    PRE_GENERATION = enum.auto()
    GENERATION = enum.auto()
    POST_GENERATION = enum.auto()

    PRE_SLOTS = enum.auto()
    SLOTS = enum.auto()
    POST_SLOTS = enum.auto()
