from pysat.solvers import Glucose42

g = Glucose42()
g.add_clause([(1,2), (1,3)])
g.add_clause([(3,4), (3,5)])
print(g.solve())
print(g.get_model())

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