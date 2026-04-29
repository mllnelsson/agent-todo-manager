from enum import StrEnum, auto


class Status(StrEnum):
    TODO = auto()
    IN_PROGRESS = auto()
    COMPLETED = auto()


class ProjectStatus(StrEnum):
    ACTIVE = auto()
    ARCHIVED = auto()


class EntityType(StrEnum):
    STORY = auto()
    TASK = auto()
    STEP = auto()


class Action(StrEnum):
    STARTED = auto()
    COMPLETED = auto()
