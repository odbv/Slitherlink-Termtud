from pysat.solvers import Glucose42
from pysat.formula import CNF
from pysat.card import CardEnc

g = Glucose42()

'''

. - .
| 2 |
. - .

  1
2   3
  4
  
vagy 1,2 vagy 1,3 vagy 1,4 vagy 2,3 vagy 2,4 vagy 3,4


  |
- . -
  |
  
  1
2   3
  4
  
1,2 vagy 1,3 vagy 1,4 vagy 2,3 vagy 2,4 vagy 3,4 vagy 0

'''

'''

(A OR B) & (C OR D)


'''

# okay so testing
# I have three lines
# let's just imagine them
# and I want one of them to be active
# or none of them

# for simplicity's sake, let's number them 1, 2, 3

# based on ChatGPT's advice, I would have to use use four variables
# A, B, C, D
# A = 1 AND NOT-2 AND NOT-3
# B = NOT-1 AND 2 AND NOT-3
# C = NOT-2 AND NOT-2 AND 3
# D = NOT-1 NOT-2 NOT-3

# with a final conjuction of A OR B OR C OR D

'''

A = 10
B = 11
C = 12
D = 13

cnf = CNF()

cnf.append([-A, 1])
cnf.append([-A, -2])
cnf.append([-A, -3])
cnf.append([-1, 2, 3, A])

cnf.append([-B, -1])
cnf.append([-B, 2])
cnf.append([-B, -3])
cnf.append([1, -2, 3, B])

cnf.append([-C, -1])
cnf.append([-C, -2])
cnf.append([-C, 3])
cnf.append([1, 2, -3, C])

cnf.append([-D, -1])
cnf.append([-D, -2])
cnf.append([-D, -3])
cnf.append([1,2,3,D])

onlyone = CardEnc.equals(lits=[A,B,C,D], bound=1, encoding=1)
for clause in onlyone.clauses:
  cnf.append(clause)

cnf.to_file("test_mini.cnf")

with Glucose42(bootstrap_with=cnf, with_proof=True) as temp:
    print(temp.solve())
    print(temp.get_model())
    #print(temp.get_proof())

'''
    
# so this works

# next experiment:
# we have some points
# and each must have 

a:int = 1
b:str = ""

b += str(a)
print(b)