# 8bit-cpu
A 8 bit CPU logic circuit

一个月前刷B站的时候看见一个宝藏教程一个8位二进制CPU的设计和实现_哔哩哔哩_bilibili，最近终于看完了，并且实现了一个8位CPU。成品是这个样子的：
![image](https://github.com/jwk000/8bit-cpu/assets/8400325/5d8b3b26-ad57-4892-823d-cda15181d850)

它能做的事情很少，但足以说明CPU的工作原理，我写了个demo用它计算斐波那契数列：

```asm
MOV SS, 0Xff
MOV SP, 0Xff

main:
MOV T1, 10
CALL fib
HLT

fib:
CMP T1, 3
JNO out1

PUSH T1
PUSH T2
PUSH T3

DEC T1
CALL fib
MOV T2, D

DEC T1
CALL fib
MOV T3, D

ADD T2, T3
MOV D, T2

POP T3
POP T2 
POP T1
RET 

out1:
MOV D, T1
RET
```

执行的结果如下（D寄存器显示89）
![image](https://github.com/jwk000/8bit-cpu/assets/8400325/0f96ac88-73a9-4bfa-8530-3d1bb37bca9a)


这就是我们的目标，下面我按照制作的步骤复述一下，希望能够讲明白。你也可以先看一下视频，但up主很多地方表达的不够清楚，这时候就可以参考我的说明了。
全文大纲
1. 简介
2. 逻辑电路入门
3. 8位加法器
4. 8位数码管
5. 8位寄存器
6. 8位程序计数器
7. 微程序
8. 8位ALU
9. 8位CPU
10. 汇编微程序
