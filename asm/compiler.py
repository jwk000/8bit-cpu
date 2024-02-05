# coding=utf-8

import os
import re
import pin
import assembly as ASM

dirname = os.path.dirname(__file__)
asmfile = os.path.join(dirname, "program.asm")
binfile = os.path.join(dirname, "program.bin")


codes = []
marks = {}  # 标签

OP2 = {
    "MOV": ASM.MOV,
    "ADD": ASM.ADD,
    "SUB": ASM.SUB,
    "AND": ASM.AND,
    "OR": ASM.OR,
    "XOR": ASM.XOR,
    "CMP": ASM.CMP,
}

OP1 = {
    "NOT": ASM.NOT,
    "INC": ASM.INC,
    "DEC": ASM.DEC,
    "PUSH": ASM.PUSH,
    "POP": ASM.POP,
    "CALL": ASM.CALL,
    "INT": ASM.INT,
    "JMP": ASM.JMP,
    "INT": ASM.INT,
    "JO": ASM.JO,
    "JNO": ASM.JNO,
    "JZ": ASM.JZ,
    "JNZ": ASM.JNZ,
    "JP": ASM.JP,
    "JNP": ASM.JNP,
}

OP0 = {
    "RET": ASM.RET,
    "HLT": ASM.HLT,
    "NOP": ASM.NOP,
    "IRET": ASM.IRET,
    "STI": ASM.STI,
    "CLI": ASM.CLI,
}

OP2SET = set(OP2.values())
OP1SET = set(OP1.values())
OP0SET = set(OP0.values())

REGISTERS = {
    "A": pin.A,
    "B": pin.B,
    "C": pin.C,
    "D": pin.D,
    "SP": pin.SP,
    "SS": pin.SS,
    "CS": pin.CS,
    "T1": pin.T1,
    "T2": pin.T2,
    "T3": pin.T3,
}


class SyntaxError(Exception):
    def __init__(self, code, msg):
        self.code = code
        self.msg = msg

    def __str__(self):
        return "SyntaxError: %s at %d" % (self.msg, self.code.number)


class Code(object):
    TYPE_CODE = 1
    TYPE_LABEL = 2

    def __init__(self, number, source: str):
        self.number = number
        self.source = source
        self.type = Code.TYPE_CODE
        self.op = None
        self.dst = None
        self.src = None
        self.parse()

    def get_op(self):
        if self.op in OP2:
            return OP2[self.op]
        if self.op in OP1:
            return OP1[self.op]
        if self.op in OP0:
            return OP0[self.op]
        raise SyntaxError(self, "unknown op %s" % self.op)

    def get_am(self, addr):  # 获取寻址方式和对应的值
        global marks
        if not addr:
            return None, None
        if addr in marks:
            return ASM.AM_INS, marks[addr]
        if addr in REGISTERS:
            return ASM.AM_REG, REGISTERS[addr]
        if re.match(r"0X\w+", addr):
            return ASM.AM_INS, int(addr, 16)
        if re.match(r"\d+", addr):
            return ASM.AM_INS, int(addr)
        match = re.match(r"\[(0X\d+)\]", addr)
        if match:
            return ASM.AM_DIR, int(match.group(1), 16)
        match = re.match(r"\[(\d+)\]", addr)
        if match:
            return ASM.AM_DIR, int(match.group(1))
        match = re.match(r"\[(\w+)\]", addr)
        if match and match.group(1) in REGISTERS:
            return ASM.AM_DIR, REGISTERS[match.group(1)]
        raise SyntaxError(self, "unknown addr mode: %s" % addr)

    def parse(self):
        match = re.match(r"\s*(\w+):", self.source)
        if match:
            self.type = Code.TYPE_LABEL
            self.op = self.source[:-1]
            return

        match = re.match(r"\s*(\w+)\s+(.+?)\s*,\s*(.+)\s*", self.source)
        if match:
            self.op = match.group(1)
            self.dst = match.group(2)
            self.src = match.group(3)
            return

        match = re.match(r"\s*(\w+)\s+(.+)\s*", self.source)
        if match:
            self.op = match.group(1)
            self.dst = match.group(2)
            return

        match = re.match(r"\s*(\w+)\s*", self.source)
        if match:
            self.op = match.group(1)
            return

    def compile(self):
        op = self.get_op()
        amd, dst = self.get_am(self.dst)
        ams, src = self.get_am(self.src)

        if op in OP2SET and (amd, ams) not in ASM.INSTRUCTIONS[2][op]:
            raise SyntaxError(self, "invalid addr2 mode")
        if op in OP1SET and amd not in ASM.INSTRUCTIONS[1][op]:
            raise SyntaxError(self, "invalid addr1 mode")
        if op in OP0SET and amd is not None:
            raise SyntaxError(self, "invalid addr0 mode")

        amd = amd or 0
        ams = ams or 0
        dst = dst or 0
        src = src or 0

        if op in OP2SET:
            ir = op | (amd << 2) | ams
        elif op in OP1SET:
            ir = op | amd
        else:
            ir = op

        return [ir, dst, src]

    def __repr__(self) -> str:
        return "%d: %s" % (self.number, self.source)


# asm代码中的注释
annotation = re.compile(r"(.*?);.*")


def compile_program():
    global codes
    global marks

    with open(asmfile, "r") as f:
        lines = f.readlines()

    for i, line in enumerate(lines):
        line = line.strip()
        line = annotation.sub(r"\1", line)
        if not line:
            continue
        code = Code(i + 1, line)
        if code.type == Code.TYPE_LABEL:
            marks[code.op] = len(codes)*3
            continue
        codes.append(code)

    codes.append(Code(len(codes) + 1, "HLT"))
    with open(binfile, "wb") as f:
        for code in codes:
            for byte in code.compile():
                f.write(byte.to_bytes(1, "little"))

def main():
    try:
        compile_program()
    except SyntaxError as e:
        print(e)

if __name__ == "__main__":
    main()
    print('compile success!')