NAME SYNTHETIC_MULTIPERIOD_PRODUCTION
ROWS
 N OBJ
 E R0
 L R1
 E R2
 L R3
 E R4
 L R5
 E R6
 L R7
 E R8
 L R9
 E R10
 L R11
 E R12
COLUMNS
 produce0 OBJ 4
 produce0 R0 1
 produce0 R1 1
 inventory0 OBJ 0.5
 inventory0 R0 -1
 inventory0 R2 1
 on0 OBJ 25
 on0 R1 -50
 produce1 OBJ 5
 produce1 R2 1
 produce1 R3 1
 inventory1 OBJ 0.5
 inventory1 R2 -1
 inventory1 R4 1
 on1 OBJ 25
 on1 R3 -50
 produce2 OBJ 3
 produce2 R4 1
 produce2 R5 1
 inventory2 OBJ 0.5
 inventory2 R4 -1
 inventory2 R6 1
 on2 OBJ 25
 on2 R5 -50
 produce3 OBJ 6
 produce3 R6 1
 produce3 R7 1
 inventory3 OBJ 0.5
 inventory3 R6 -1
 inventory3 R8 1
 on3 OBJ 25
 on3 R7 -50
 produce4 OBJ 4
 produce4 R8 1
 produce4 R9 1
 inventory4 OBJ 0.5
 inventory4 R8 -1
 inventory4 R10 1
 on4 OBJ 25
 on4 R9 -50
 produce5 OBJ 5
 produce5 R10 1
 produce5 R11 1
 inventory5 OBJ 0.5
 inventory5 R10 -1
 inventory5 R12 1
 on5 OBJ 25
 on5 R11 -50
RHS
 B R0 18
 B R1 0
 B R2 32
 B R3 0
 B R4 24
 B R5 0
 B R6 40
 B R7 0
 B R8 16
 B R9 0
 B R10 30
 B R11 0
 B R12 0
BOUNDS
 LO B produce0 0
 UP B produce0 50
 LO B inventory0 0
 UP B inventory0 100
 BV B on0
 LO B produce1 0
 UP B produce1 50
 LO B inventory1 0
 UP B inventory1 100
 BV B on1
 LO B produce2 0
 UP B produce2 50
 LO B inventory2 0
 UP B inventory2 100
 BV B on2
 LO B produce3 0
 UP B produce3 50
 LO B inventory3 0
 UP B inventory3 100
 BV B on3
 LO B produce4 0
 UP B produce4 50
 LO B inventory4 0
 UP B inventory4 100
 BV B on4
 LO B produce5 0
 UP B produce5 50
 LO B inventory5 0
 UP B inventory5 100
 BV B on5
ENDATA
