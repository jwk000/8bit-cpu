# coding=utf-8
import os
import pin
import assembly as ASM

dirname = os.path.dirname(__file__)
filename = os.path.join(dirname, "micro.bin")


CJMPS = [ASM.JO, ASM.JNO, ASM.JZ, ASM.JNZ, ASM.JP, ASM.JNP]
micro=[pin.HLT for i in range(0x10000)]

# pws从低到高依次是：溢出，零，奇偶
def compile_jump(code, op, psw):
    overflow = psw & 1
    zero = psw & 2
    parity = psw & 4

    if op == ASM.JO and overflow:
        return code
    if op == ASM.JNO and not overflow:
        return code
    if op == ASM.JZ and zero:
        return code
    if op == ASM.JNZ and not zero:
        return code
    if op == ASM.JP and parity:
        return code
    if op == ASM.JNP and not parity:
        return code
    return ASM.INSTRUCTIONS[0][ASM.NOP]


# 编译中断指令
def compile_int(code, op, psw):
    interrupt = psw & 8  # 中断开的时候才响应中断
    if op == ASM.INT and interrupt:
        return code
    return ASM.INSTRUCTIONS[0][ASM.NOP]


# 编译二地址指令
def compile_addr2(addr, ir, psw, index):
    global micro
    global CJMPS

    op = ir & 0xF0  # 高4位是操作码
    amd = (ir >> 2) & 3  # 中间2位是dst寻址方式
    ams = ir & 3  # 低2位是源操作数的寻址方式

    INST = ASM.INSTRUCTIONS[2]  # 二地址指令
    if op not in INST:
        micro[addr] = pin.CYC
        return

    am = (amd, ams)
    if am not in INST[op]:
        micro[addr] = pin.CYC
        return

    code = INST[op][am]

    if index < len(code):
        micro[addr] = code[index]
    else:
        micro[addr] = pin.CYC


# 编译一地址指令
def compile_addr1(addr, ir, psw, index):
    global micro

    op = ir & 0xFC  # 高6位是操作码
    amd = ir & 3  # 低2位是dst寻址方式

    INST = ASM.INSTRUCTIONS[1]  # 一地址指令
    if op not in INST:
        micro[addr] = pin.CYC
        return

    am = amd
    if am not in INST[op]:
        micro[addr] = pin.CYC
        return

    code = INST[op][am]
    if op in CJMPS:
        code = compile_jump(code, op, psw)
    elif op == ASM.INT:
        code = compile_int(code, op, psw)

    if index < len(code):
        micro[addr] = code[index]
    else:
        micro[addr] = pin.CYC


# 编译零地址指令
def compile_addr0(addr, ir, psw, index):
    global micro

    op = ir & 0xFF  # 操作码

    INST = ASM.INSTRUCTIONS[0]  # 零地址指令
    if op not in INST:
        micro[addr] = pin.CYC
        return

    code = INST[op]
    if index < len(code):
        micro[addr] = code[index]
    else:
        micro[addr] = pin.CYC


def main():
    global micro

    # 填充微程序，16位地址，高8位是ir，低8位是psw和index
    for i in range(0x10000):
        ir = i >> 8 #指令
        psw = (i >> 4) & 0xF #状态字
        cyc = i & 0xf #微指令序号

        #每个指令周期前6条微指令都是取指令
        if cyc < len(ASM.FETCH):
            micro[i] = ASM.FETCH[cyc]
            continue

        index = cyc - len(ASM.FETCH) #微指令序号

        if ir & ASM.ADDR2:
            compile_addr2(i, ir, psw, index)
        elif ir & ASM.ADDR1:
            compile_addr1(i, ir, psw, index)
        else:
            compile_addr0(i, ir, psw, index)

    # 写入文件
    with open(filename, "wb") as f:
        for i in range(0x10000):
            f.write(micro[i].to_bytes(4, "little"))

if __name__ == "__main__":
    main()
    print('compile success!')
