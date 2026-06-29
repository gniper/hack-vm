import sys
from lib.parser import parser
from lib.code_writer import code_writer

if len(sys.argv) < 2:
    print("Usage: python vm.py <program_file>")
    sys.exit(1)

input_file = sys.argv[1]
assm_output = []


if len(sys.argv) >= 3:
    output_file = sys.argv[2]
else: 
    output_file = (input_file.split(".")[0] + ".asm").capitalize()


cmds = parser(input_file)
code_writer(output_file, cmds)

