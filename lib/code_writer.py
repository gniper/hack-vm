import sys
from lib.cmd_type import CmdType, Type, SEGMENT_MAP, Segment

TEMP = 5

def pointer_symbol(i):
    match int(i):
        case 0:
            return "THIS"
        case 1:
            return "THAT"
        case _:
            raise ValueError("pointer segment index must be 0 or 1")

def push_write(file_name, segment, i):
    lines = []
    if segment == Segment.CONSTANT:
        lines.append(f"// push constant {i}: VM constants are immediate values, so no memory lookup is needed")
        lines.append(f"@{i}")
        lines.append("D=A")
        lines.append("// push: SP points at the next free stack slot")
        lines.append("@SP")
        lines.append("A=M")
        lines.append("M=D")
        lines.append("// push: advance SP so the next value is not overwritten")
        lines.append("@SP")
        lines.append("M=M+1")
    else:
        if segment in {Segment.LOCAL, Segment.ARGUMENT, Segment.THIS, Segment.THAT}:
            seg = SEGMENT_MAP[segment]
            lines.append(f"// push {segment.value} {i}: this segment is addressed relative to its base pointer")
            lines.append(f"@{i}")
            lines.append("D=A")
            lines.append(f"@{seg}")
            lines.append("A=D+M")
        elif segment == Segment.POINTER:
            seg = pointer_symbol(i)
            lines.append(f"// push pointer {i}: pointer indexes expose THIS/THAT directly")
            lines.append(f"@{seg}")
        elif segment == Segment.STATIC:
            addr = file_name + "." + i
            lines.append(f"// push static {i}: static variables need a file-scoped symbol")
            lines.append(f"@{i}")
            lines.append("D=A")
            lines.append(f"@{addr}")
            lines.append("A=D+A")
        elif segment == Segment.TEMP:
            addr = 5
            lines.append(f"// push temp {i}: temp lives at fixed RAM addresses starting at R5")
            lines.append(f"@{i}")
            lines.append("D=A")
            lines.append(f"@{addr}")
            lines.append("A=D+A")
        lines.append("D=M")
        lines.append("// push: SP points at the next free stack slot")
        lines.append("@SP")
        lines.append("A=M")
        lines.append("M=D")
        lines.append("// push: advance SP so the next value is not overwritten")
        lines.append("@SP")
        lines.append("M=M+1")
    return lines

def pop_write(file_name, segment, i):
    if (segment == "constant"):
        raise ValueError("cannot pop into constant!")
    lines = []
    

    if segment in {Segment.LOCAL, Segment.ARGUMENT, Segment.THIS, Segment.THAT}:
        seg = SEGMENT_MAP[segment]
        lines.append(f"// pop {segment.value} {i}: compute the target address before SP is reused")
        lines.append(f"@{i}")
        lines.append("D=A")
        lines.append(f"@{seg}")
        lines.append("D=D+M")
    elif segment == Segment.POINTER:
        seg = pointer_symbol(i)
        lines.append(f"// pop pointer {i}: pointer writes replace THIS/THAT themselves")
        lines.append(f"@{seg}")
        lines.append("D=A")
    elif segment == Segment.STATIC:
        addr = file_name + "." + i
        lines.append(f"// pop static {i}: static variables need a file-scoped symbol")
        lines.append(f"@{i}")
        lines.append("D=A")
        lines.append(f"@{addr}")
        lines.append("D=D+A")
    elif segment == Segment.TEMP:
        addr = 5
        lines.append(f"// pop temp {i}: temp lives at fixed RAM addresses starting at R5")
        lines.append(f"@{i}")
        lines.append("D=A")
        lines.append(f"@{addr}")
        lines.append("D=D+A")
    lines.append("// pop: keep the target address because popping changes A and D")
    lines.append("@R13")
    lines.append("M=D")
    lines.append("// pop: SP is moved back first because it points one past the top value")
    lines.append("@SP")
    lines.append("M=M-1")
    lines.append("A=M")
    lines.append("D=M")
    lines.append("@R13")
    lines.append("A=M")
    lines.append("M=D")
    return lines

def add_write():
    lines = []
    lines.append("// add: consume two stack values and leave one result")
    lines.append("@SP")
    lines.append("M=M-1")
    lines.append("A=M")
    lines.append("D=M")
    lines.append("@SP")
    lines.append("M=M-1")
    lines.append("A=M")
    lines.append("D=D+M")
    lines.append("M=D")
    lines.append("@SP")
    lines.append("M=M+1")
    return lines

def sub_write():
    lines = []
    lines.append("// sub: preserve operand order because VM subtraction is x - y")
    lines.append("@SP")
    lines.append("M=M-1")
    lines.append("A=M")
    lines.append("D=M")
    lines.append("@SP")
    lines.append("M=M-1")
    lines.append("A=M")
    lines.append("D=M-D")
    lines.append("M=D")
    lines.append("@SP")
    lines.append("M=M+1")
    return lines

def neg_write():
    lines = []
    lines.append("// neg: unary operations update the current top value in place")
    lines.append("@SP")
    lines.append("A=M-1")
    lines.append("M=-M")
    return lines

def eq_write(label_id):
    true_label = f"EQUAL{label_id}"
    end_label = f"END{label_id}"
    lines = []
    lines.append("// eq: compare the top two values and collapse them into one boolean")
    lines.append("@SP")
    lines.append("A=M-1")
    lines.append("D=M")
    lines.append("A=A-1")
    lines.append("D=M-D")
    lines.append("// eq: unique labels keep separate comparisons from sharing jump targets")
    lines.append(f"@{true_label}")
    lines.append("D;JEQ")
    lines.append("@SP")
    lines.append("M=M-1")
    lines.append("A=M-1")
    lines.append("M=0")
    lines.append(f"@{end_label}")
    lines.append("0;JMP")
    lines.append(f"({true_label})")
    lines.append("@SP")
    lines.append("M=M-1")
    lines.append("A=M-1")
    lines.append("M=-1")
    lines.append(f"({end_label})")
    return lines

def gt_write(label_id):
    true_label = f"GREAT{label_id}"
    end_label = f"END{label_id}"
    lines = []
    lines.append("// gt: compare x - y because VM order is second-from-top greater than top")
    lines.append("@SP")
    lines.append("A=M-1")
    lines.append("D=M")
    lines.append("A=A-1")
    lines.append("D=M-D")
    lines.append("// gt: unique labels keep separate comparisons from sharing jump targets")
    lines.append(f"@{true_label}")
    lines.append("D;JGT")
    lines.append("@SP")
    lines.append("M=M-1")
    lines.append("A=M-1")
    lines.append("M=0")
    lines.append(f"@{end_label}")
    lines.append("0;JMP")
    lines.append(f"({true_label})")
    lines.append("@SP")
    lines.append("M=M-1")
    lines.append("A=M-1")
    lines.append("M=-1")
    lines.append(f"({end_label})")
    return lines

def lt_write(label_id):
    true_label = f"LESS{label_id}"
    end_label = f"END{label_id}"
    lines = []
    lines.append("// lt: compare x - y because VM order is second-from-top less than top")
    lines.append("@SP")
    lines.append("A=M-1")
    lines.append("D=M")
    lines.append("A=A-1")
    lines.append("D=M-D")
    lines.append("// lt: unique labels keep separate comparisons from sharing jump targets")
    lines.append(f"@{true_label}")
    lines.append("D;JLT")
    lines.append("@SP")
    lines.append("M=M-1")
    lines.append("A=M-1")
    lines.append("M=0")
    lines.append(f"@{end_label}")
    lines.append("0;JMP")
    lines.append(f"({true_label})")
    lines.append("@SP")
    lines.append("M=M-1")
    lines.append("A=M-1")
    lines.append("M=-1")
    lines.append(f"({end_label})")
    return lines

def and_write():
    lines = []
    lines.append("// and: binary logical operations consume two values and leave one result")
    lines.append("@SP")
    lines.append("A=M-1")
    lines.append("D=M")
    lines.append("A=A-1")
    lines.append("M=D&M")
    lines.append("@SP")
    lines.append("M=M-1")
    return lines

def or_write():
    lines = []
    lines.append("// or: binary logical operations consume two values and leave one result")
    lines.append("@SP")
    lines.append("A=M-1")
    lines.append("D=M")
    lines.append("A=A-1")
    lines.append("M=D|M")
    lines.append("@SP")
    lines.append("M=M-1")
    return lines

def not_write():
    lines = []
    lines.append("// not: unary operations update the current top value in place")
    lines.append("@SP")
    lines.append("A=M-1")
    lines.append("M=!M")
    return lines


def code_writer(output_file, cmds):
    lines = []
    label_id = 0
    for c in cmds:
        if c.type == Type.SO:
            match c.cmd:
                case CmdType.PUSH:
                    lines.extend(push_write(output_file.split(".")[0], c.segment, c.i))
                case CmdType.POP:
                    lines.extend(pop_write(output_file.split(".")[0], c.segment, c.i))
        elif c.type == Type.ALO:
            match c.cmd:
                case CmdType.ADD:
                    lines.extend(add_write())
                case CmdType.SUB:
                    lines.extend(sub_write())
                case CmdType.NEG:
                    lines.extend(neg_write())
                case CmdType.EQ:
                    lines.extend(eq_write(label_id))
                    label_id += 1
                case CmdType.GT:
                    lines.extend(gt_write(label_id))
                    label_id += 1
                case CmdType.LT:
                    lines.extend(lt_write(label_id))
                    label_id += 1
                case CmdType.AND:
                    lines.extend(and_write())
                case CmdType.OR:
                    lines.extend(or_write())
                case CmdType.NOT:
                    lines.extend(not_write())
    try:
        with open(output_file, "w") as f:
            f.write("\n".join(lines))
    except PermissionError:
        print(f"Error: no permission to create '{output_file}")
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}")
        sys.exit(1)
