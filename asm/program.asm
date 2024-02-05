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
