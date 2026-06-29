import sys

from lib.cmd_type import CmdType, Segment, Cmd, Type 

def parser (input_file):
    cmds = []
    try:
        with open(input_file, "r") as f:
            for line in f:
                s_line = line.strip()
                if not s_line or s_line.startswith("//"):
                    continue
                if s_line.startswith("pop"):
                    cmd = s_line.split()
                    cmds.append(Cmd(Type.SO, CmdType.POP, Segment(cmd[1]), cmd[2]))
                elif s_line.startswith("push"):
                    cmd = s_line.split()
                    cmds.append(Cmd(Type.SO, CmdType.PUSH, Segment(cmd[1]), cmd[2]))
                elif s_line.startswith("add"):
                    cmds.append(Cmd(Type.ALO, CmdType.ADD))
                elif s_line.startswith("sub"):
                    cmds.append(Cmd(Type.ALO, CmdType.SUB))
                elif s_line.startswith("neg"):
                    cmds.append(Cmd(Type.ALO, CmdType.NEG))
                elif s_line.startswith("eq"):
                    cmds.append(Cmd(Type.ALO, CmdType.EQ))
                elif s_line.startswith("gt"):
                    cmds.append(Cmd(Type.ALO, CmdType.GT))
                elif s_line.startswith("lt"):
                    cmds.append(Cmd(Type.ALO, CmdType.LT))
                elif s_line.startswith("and"):
                    cmds.append(Cmd(Type.ALO, CmdType.AND))
                elif s_line.startswith("or"):
                    cmds.append(Cmd(Type.ALO, CmdType.OR))
                elif s_line.startswith("not"):
                    cmds.append(Cmd(Type.ALO, CmdType.NOT))
               
        return cmds
    except FileNotFoundError:
        print(f"Error: file '{input_file}' not found")
        sys.exit(1)
    except PermissionError:
        print(f"Error: no permission to read '{input_file}")
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}")
        sys.exit(1)
