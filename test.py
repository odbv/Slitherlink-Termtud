from pysat.solvers import Glucose42

g = Glucose42()
g.add_clause([-1, 2])
g.add_clause([-2, 3])
print(g.solve())
print(g.get_model())