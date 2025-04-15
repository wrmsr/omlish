import enum


class ProcessorPriority(enum.IntEnum):
    BOOTSTRAP = enum.auto()
    PRE_GENERATION = enum.auto()
    GENERATION = enum.auto()
    POST_GENERATION = enum.auto()
    SLOTS = enum.auto()
