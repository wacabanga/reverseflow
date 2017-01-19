"""These are arrows for control flow of input"""
from arrows.primitivearrow import PrimitiveArrow
from typing import List, MutableMapping, Set
from sympy import Expr, Eq, Rel



class DuplArrow(PrimitiveArrow):
    """
    Duplicate input
    f(x) = (x, x, ..., x)
    """
    def __init__(self, n_duplications=2):
        name = 'Dupl'
        super().__init__(n_in_ports=1, n_out_ports=n_duplications, name=name)

    def gen_constraints(self, input_expr: MutableMapping[int, Expr], output_expr: MutableMapping[int, Expr]) -> Set[Rel]:
        constraints = []
        for i in output_expr.keys():
            for j in output_expr.keys():
                if i != j:
                    constraints.append(Eq(output_expr[i], output_expr[j]))
        return constraints


class InvDuplArrow(PrimitiveArrow):
    """InvDupl f(x1,...,xn) = x"""

    def __init__(self, n_duplications=2):
        name = "InvDupl"
        super().__init__(n_in_ports=n_duplications, n_out_ports=1, name=name)

    def gen_constraints(self, input_expr: MutableMapping[int, Expr], output_expr: MutableMapping[int, Expr]) -> List[Rel]:
        assert 0 in output_expr
        constraints = []
        for i in input_expr.keys():
            constraints.append(Eq(output_expr[0], input_expr[i]))
        return constraints


class IdentityArrow(PrimitiveArrow):
    """
    Identity input
    f(x) = x
    """

    def __init__(self) -> None:
        name = 'Identity'
        super().__init__(n_in_ports=1, n_out_ports=1, name=name)
