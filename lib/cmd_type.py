from enum import Enum


class Type(Enum):
    ALO = "ALO" # Arithmetic LogIcal Operation, ADD, SUB
    SO = "SO" # Stack Operation, PUSH, POP

class CmdType(Enum):
    PUSH = "push"
    POP = "pop"
    ADD = "add"
    SUB = "sub"
    NEG = "neg"
    EQ = "eq"
    GT = "gt"
    LT = "lt"
    AND = "and"
    OR = "or"
    NOT = "not"

class Segment(Enum):
    LOCAL = "local"
    ARGUMENT = "argument"
    THIS="this"
    THAT="that"
    POINTER="pointer"
    TEMP="temp"
    CONSTANT = "constant"
    STATIC = "static"

SEGMENT_MAP = {
    Segment.LOCAL:    "LCL",
    Segment.ARGUMENT: "ARG",
    Segment.THIS:     "THIS",
    Segment.THAT:     "THAT",
}

class Cmd:
    def __init__(self, type, cmd, segment=None, i=None):
        self.type = type
        self.cmd = cmd
        self.segment = segment
        self.i = i

    def __repr__(self):
        return f"Cmd(type={self.type}, cmd={self.cmd}, segment={self.segment}, i={self.i})"