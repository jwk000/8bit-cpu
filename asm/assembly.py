# coding=utf8
# 汇编指令的微程序表示
import pin

# 取指令微程序
FETCH = [
    pin.PC_OUT | pin.MAR_IN,  # 程序计数器值送地址寄存器
    pin.MC_OUT | pin.IR_IN | pin.PC_INC,  # 内存控制器取指令，送指令寄存器，程序计数器加1
    pin.PC_OUT | pin.MAR_IN,  # 程序计数器值送地址寄存器
    pin.MC_OUT | pin.DST_IN | pin.PC_INC,  # 内存控制器取指令，送目的操作数寄存器，程序计数器加1
    pin.PC_OUT | pin.MAR_IN,  # 程序计数器值送地址寄存器
    pin.MC_OUT | pin.SRC_IN | pin.PC_INC,  # 内存控制器取指令，送源操作数寄存器，程序计数器加1
]


ADDR2 = 1 << 7  # 2地址指令最高位是1
ADDR1 = 1 << 6  # 1地址指令最高位是01
ADDR0 = 0  # 0地址指令最高位是00

# 2地址指令格式 1aaabbcc aaa指令码，bb目的操作数寻址方式，cc源操作数寻址方式
# 有3位指令码，所以最多有8条指令，有2位操作数寻址方式，所以最多有4种寻址方式
ADDR2_SHIFT = 4

# 1地址指令格式 01aaaabb aaaa指令码，bb操作数寻址方式
ADDR1_SHIFT = 2

# 寻址方式
AM_INS = 0  # 立即寻址
AM_REG = 1  # 寄存器寻址
AM_DIR = 2  # 直接寻址
AM_RAM = 3  # 间接寻址

# 2地址指令 最多支持8条指令
MOV = ADDR2 | (0 << ADDR2_SHIFT)
ADD = ADDR2 | (1 << ADDR2_SHIFT)
SUB = ADDR2 | (2 << ADDR2_SHIFT)
CMP = ADDR2 | (3 << ADDR2_SHIFT)
AND = ADDR2 | (4 << ADDR2_SHIFT)
OR = ADDR2 | (5 << ADDR2_SHIFT)
XOR = ADDR2 | (6 << ADDR2_SHIFT)

# 1地址指令 最多支持16条指令
INC = ADDR1 | (0 << ADDR1_SHIFT)
DEC = ADDR1 | (1 << ADDR1_SHIFT)
NOT = ADDR1 | (2 << ADDR1_SHIFT)
JMP = ADDR1 | (3 << ADDR1_SHIFT)
JO = ADDR1 | (4 << ADDR1_SHIFT)  # 溢出跳转
JNO = ADDR1 | (5 << ADDR1_SHIFT)  # 不溢出跳转
JZ = ADDR1 | (6 << ADDR1_SHIFT)  # 零跳转
JNZ = ADDR1 | (7 << ADDR1_SHIFT)  # 非零跳转
JP = ADDR1 | (8 << ADDR1_SHIFT)  # 正跳转
JNP = ADDR1 | (9 << ADDR1_SHIFT)  # 非正跳转
PUSH = ADDR1 | (10 << ADDR1_SHIFT)
POP = ADDR1 | (11 << ADDR1_SHIFT)
CALL = ADDR1 | (12 << ADDR1_SHIFT)
INT = ADDR1 | (13 << ADDR1_SHIFT)

# 0地址指令
NOP = 0  # 空指令
RET = 1  # 返回
IRET = 2  # 中断返回
STI = 3  # 开中断
CLI = 4  # 关中断
HLT = 0x3F  # 停机


INSTRUCTIONS = {
    2: {
        MOV: {
            (AM_REG, AM_INS): [
                pin.DST_W | pin.SRC_OUT,  # SRC的值写入DST指向的寄存器
            ],
            (AM_REG, AM_REG): [
                pin.DST_W | pin.SRC_R,  # SRC指向的寄存器的值写入DST指向的寄存器
            ],
            (AM_REG, AM_DIR): [
                pin.MAR_IN | pin.SRC_OUT,  # src的值写入mar
                pin.MC_OUT | pin.DST_W,  # mar指向的内存单元的值写入DST指向的寄存器
            ],
            (AM_REG, AM_RAM): [
                pin.MAR_IN | pin.SRC_R,  # src指向的寄存器的值写入mar
                pin.MC_OUT | pin.DST_W,  # mar指向的内存单元的值送DST指向的寄存器
            ],
            (AM_DIR, AM_INS): [
                pin.MAR_IN | pin.DST_OUT,  # DST指向的内存单元的地址送地址寄存器
                pin.MC_IN | pin.SRC_OUT,  # SRC的值送内存
            ],
            (AM_DIR, AM_REG): [
                pin.MAR_IN | pin.DST_OUT,  # DST指向的内存单元的地址送地址寄存器
                pin.MC_IN | pin.SRC_R,  # SRC指向的寄存器的值送内存控制器
            ],
            (AM_DIR, AM_DIR): [
                pin.MAR_IN | pin.DST_OUT,  # DST指向的内存单元的地址送地址寄存器
                pin.T1_IN | pin.SRC_OUT,  # SRC指向的内存单元的值送数据寄存器
                pin.MC_IN | pin.T1_OUT,
            ],
            (AM_DIR, AM_RAM): [
                pin.MAR_IN | pin.SRC_R,
                pin.T1_IN | pin.MC_OUT,
                pin.MAR_IN | pin.DST_OUT,
                pin.MC_IN | pin.T1_OUT,
            ],
            (AM_RAM, AM_INS): [
                pin.MAR_IN | pin.DST_R,  # DST指向的内存单元的地址送地址寄存器
                pin.MC_IN | pin.SRC_OUT,  # SRC的值送内存
            ],
            (AM_RAM, AM_REG): [
                pin.MAR_IN | pin.DST_R,  # DST指向的内存单元的地址送地址寄存器
                pin.MC_IN | pin.SRC_R,  # SRC指向的寄存器的值送内存控制器
            ],
            (AM_RAM, AM_DIR): [
                pin.MAR_IN | pin.DST_R,  # DST指向的内存单元的地址送地址寄存器
                pin.T1_IN | pin.SRC_OUT,  # SRC指向的内存单元的值送数据寄存器
                pin.MC_IN | pin.T1_OUT,
            ],
            (AM_RAM, AM_RAM): [
                pin.MAR_IN | pin.SRC_R,
                pin.T1_IN | pin.MC_OUT,
                pin.MAR_IN | pin.DST_R,
                pin.MC_IN | pin.T1_OUT,
            ],
        },
        ADD: {
            (AM_REG, AM_INS): [
                pin.A_IN | pin.SRC_OUT,
                pin.B_IN | pin.DST_R,
                pin.ALU_OP_ADD
                | pin.ALU_OUT
                | pin.ALU_PSW
                | pin.DST_W,  # A+B的值送DST指向的寄存器
            ],
            (AM_REG, AM_REG): [
                pin.A_IN | pin.SRC_R,
                pin.B_IN | pin.DST_R,
                pin.ALU_OP_ADD
                | pin.ALU_OUT
                | pin.ALU_PSW
                | pin.DST_W,  # A+B的值送DST指向的寄存器
            ],
        },
        SUB: {
            (AM_REG, AM_INS): [
                pin.A_IN | pin.SRC_OUT,
                pin.B_IN | pin.DST_R,
                pin.ALU_OP_SUB
                | pin.ALU_OUT
                | pin.ALU_PSW
                | pin.DST_W,  # A-B的值送DST指向的寄存器
            ],
            (AM_REG, AM_REG): [
                pin.A_IN | pin.SRC_R,
                pin.B_IN | pin.DST_R,
                pin.ALU_OP_SUB
                | pin.ALU_OUT
                | pin.ALU_PSW
                | pin.DST_W,  # A-B的值送DST指向的寄存器
            ],
        },
        CMP: {
            (AM_REG, AM_INS): [
                pin.A_IN | pin.SRC_OUT,
                pin.B_IN | pin.DST_R,
                pin.ALU_OP_SUB | pin.ALU_PSW,  # A-B的PSW
            ],
            (AM_REG, AM_REG): [
                pin.A_IN | pin.SRC_R,
                pin.B_IN | pin.DST_R,
                pin.ALU_OP_SUB | pin.ALU_PSW,  # A-B的PSW
            ],
        },
        AND: {
            (AM_REG, AM_INS): [
                pin.A_IN | pin.SRC_OUT,
                pin.B_IN | pin.DST_R,
                pin.ALU_OP_AND
                | pin.ALU_OUT
                | pin.ALU_PSW
                | pin.DST_W,  # A&B的值送DST指向的寄存器
            ],
            (AM_REG, AM_REG): [
                pin.A_IN | pin.SRC_R,
                pin.B_IN | pin.DST_R,
                pin.ALU_OP_AND
                | pin.ALU_OUT
                | pin.ALU_PSW
                | pin.DST_W,  # A&B的值送DST指向的寄存器
            ],
        },
        OR: {
            (AM_REG, AM_INS): [
                pin.A_IN | pin.SRC_OUT,
                pin.B_IN | pin.DST_R,
                pin.ALU_OP_OR
                | pin.ALU_OUT
                | pin.ALU_PSW
                | pin.DST_W,  # A|B的值送DST指向的寄存器
            ],
            (AM_REG, AM_REG): [
                pin.A_IN | pin.SRC_R,
                pin.B_IN | pin.DST_R,
                pin.ALU_OP_OR
                | pin.ALU_OUT
                | pin.ALU_PSW
                | pin.DST_W,  # A|B的值送DST指向的寄存器
            ],
        },
        XOR: {
            (AM_REG, AM_INS): [
                pin.A_IN | pin.SRC_OUT,
                pin.B_IN | pin.DST_R,
                pin.ALU_OP_XOR
                | pin.ALU_OUT
                | pin.ALU_PSW
                | pin.DST_W,  # A^B的值送DST指向的寄存器
            ],
            (AM_REG, AM_REG): [
                pin.A_IN | pin.SRC_R,
                pin.B_IN | pin.DST_R,
                pin.ALU_OP_XOR
                | pin.ALU_OUT
                | pin.ALU_PSW
                | pin.DST_W,  # A^B的值送DST指向的寄存器
            ],
        },
    },
    1: {
        INC: {
            AM_REG: [
                pin.A_IN | pin.DST_R,
                pin.ALU_OP_INC
                | pin.ALU_OUT
                | pin.ALU_PSW
                | pin.DST_W,  # A+1的值送DST指向的寄存器
            ],
        },
        DEC: {
            AM_REG: [
                pin.A_IN | pin.DST_R,
                pin.ALU_OP_DEC
                | pin.ALU_OUT
                | pin.ALU_PSW
                | pin.DST_W,  # A-1的值送DST指向的寄存器
            ],
        },
        NOT: {
            AM_REG: [
                pin.A_IN | pin.DST_R,
                pin.ALU_OP_NOT
                | pin.ALU_OUT
                | pin.ALU_PSW
                | pin.DST_W,  # ~A的值送DST指向的寄存器
            ],
        },
        JMP: {
            AM_INS: [
                pin.DST_OUT | pin.PC_IN,  # 内存控制器取指令，送指令寄存器
            ],
        },
        JO: {
            AM_INS: [
                pin.DST_OUT | pin.PC_IN,
            ]
        },
        JNO: {
            AM_INS: [
                pin.DST_OUT | pin.PC_IN,
            ]
        },
        JZ: {
            AM_INS: [
                pin.DST_OUT | pin.PC_IN,
            ]
        },
        JNZ: {
            AM_INS: [
                pin.DST_OUT | pin.PC_IN,
            ]
        },
        JP: {
            AM_INS: [
                pin.DST_OUT | pin.PC_IN,
            ]
        },
        JNP: {
            AM_INS: [
                pin.DST_OUT | pin.PC_IN,
            ]
        },
        PUSH: {  # SP指向栈顶，栈地址向下增长
            AM_INS: [
                pin.SP_OUT | pin.A_IN,  # SP-1
                pin.ALU_OP_DEC | pin.ALU_OUT | pin.SP_IN,
                pin.SP_OUT | pin.MAR_IN,
                pin.SS_OUT | pin.MSR_IN,  # 切换堆栈段
                pin.MC_IN | pin.DST_OUT,  # 立即数压栈
                pin.CS_OUT | pin.MSR_IN,  # 切换代码段
            ],
            AM_REG: [
                pin.SP_OUT | pin.A_IN,  # SP-1
                pin.ALU_OP_DEC | pin.ALU_OUT | pin.SP_IN,
                pin.SP_OUT | pin.MAR_IN,
                pin.SS_OUT | pin.MSR_IN,
                pin.MC_IN | pin.DST_R,  # 寄存器的值压栈
                pin.CS_OUT | pin.MSR_IN,
            ],
        },
        POP: {
            AM_REG: [
                pin.SP_OUT | pin.MAR_IN,
                pin.SS_OUT | pin.MSR_IN,
                pin.MC_OUT | pin.DST_W,  # 栈顶的值送寄存器
                pin.CS_OUT | pin.MSR_IN,
                pin.SP_OUT | pin.A_IN,  # SP+1
                pin.ALU_OP_INC | pin.ALU_OUT | pin.SP_IN,
            ],
        },
        CALL: {
            AM_INS: [
                pin.SP_OUT | pin.A_IN,  # SP-1
                pin.ALU_OP_DEC | pin.ALU_OUT | pin.SP_IN,
                pin.SP_OUT | pin.MAR_IN,
                pin.SS_OUT | pin.MSR_IN,  # 切换堆栈段
                pin.MC_IN | pin.PC_OUT,  # PC压栈
                pin.PC_IN | pin.DST_OUT,  # 立即数送PC
                pin.CS_OUT | pin.MSR_IN,  # 切换代码段
            ],
            AM_REG: [
                pin.SP_OUT | pin.A_IN,  # SP-1
                pin.ALU_OP_DEC | pin.ALU_OUT | pin.SP_IN,
                pin.SP_OUT | pin.MAR_IN,
                pin.SS_OUT | pin.MSR_IN,  # 切换堆栈段
                pin.MC_IN | pin.PC_OUT,  # PC压栈
                pin.CS_OUT | pin.MSR_IN,  # 切换代码段
                pin.PC_IN | pin.DST_R,  # 立即数送PC
            ],
        },
        INT: {
            AM_INS: [
                pin.SP_OUT | pin.A_IN,  # SP-1
                pin.ALU_OP_DEC | pin.ALU_OUT | pin.SP_IN,
                pin.SP_OUT | pin.MAR_IN,
                pin.SS_OUT | pin.MSR_IN,  # 切换堆栈段
                pin.MC_IN | pin.PC_OUT,  # PC压栈
                pin.PC_IN | pin.DST_OUT,  # 立即数送PC
                pin.CS_OUT | pin.MSR_IN |pin.ALU_PSW|pin.ALU_CLI,  # 切换代码段，读取程序状态字，关中断
            ],
            AM_REG: [
                pin.SP_OUT | pin.A_IN,  # SP-1
                pin.ALU_OP_DEC | pin.ALU_OUT | pin.SP_IN,
                pin.SP_OUT | pin.MAR_IN,
                pin.SS_OUT | pin.MSR_IN,  # 切换堆栈段
                pin.MC_IN | pin.PC_OUT,  # PC压栈
                pin.PC_IN | pin.DST_R,  # 寄存器值送PC
                pin.CS_OUT | pin.MSR_IN |pin.ALU_PSW|pin.ALU_CLI,  # 切换代码段，读取程序状态字，关中断
            ],
        },
    },
    0:{
        NOP:[
            pin.CYC, #指令周期结束
        ],
        RET:[
            pin.SP_OUT|pin.MAR_IN,
            pin.SS_OUT|pin.MSR_IN,
            pin.MC_OUT|pin.PC_IN,
            pin.CS_OUT|pin.MSR_IN,
            pin.SP_OUT|pin.A_IN, #SP+1
            pin.ALU_OP_INC|pin.ALU_OUT|pin.SP_IN,
        ],
        IRET:[
            pin.SP_OUT|pin.MAR_IN,
            pin.SS_OUT|pin.MSR_IN,
            pin.MC_OUT|pin.PC_IN,
            pin.SP_OUT|pin.A_IN, #SP+1
            pin.ALU_OP_INC|pin.ALU_OUT|pin.SP_IN,
            pin.CS_OUT|pin.MSR_IN|pin.ALU_PSW|pin.ALU_STI, #切换代码段，读取程序状态字，开中断
        ],
        STI:[
            pin.ALU_PSW|pin.ALU_STI,
        ],
        CLI:[
            pin.ALU_PSW|pin.ALU_CLI,
        ],
        HLT:[
            pin.HLT
        ]
    }
}
