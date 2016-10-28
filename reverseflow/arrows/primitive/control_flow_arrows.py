"""These are arrows for control flow of input"""

from typing import List, Dict

from sympy import Expr

from reverseflow.arrows.primitivearrow import PrimitiveArrow


class DuplArrow(PrimitiveArrow):
    """
    Duplicate input
    f(x) = (x, x, ..., x)
    """
    def __init__(self, n_duplications=2):
        name = 'Dupl'
        super().__init__(n_in_ports=1, n_out_ports=n_duplications, name=name)

    def gen_constraints(self, input_expr: Dict[int, Expr], output_expr: Dict[int, Expr]) -> List[Expr]:
        constraints = []
        if 0 in output_expr and 1 in output_expr:
            constraints.append(output_expr[0] - output_expr[1])
        if 0 in output_expr and 0 in input_expr:
            constraints.append(output_expr[0] - input_expr[0])
        if 1 in output_expr and 0 in input_expr:
            constraints.append(output_expr[1] - input_expr[0])
        return constraints


class IdentityArrow(PrimitiveArrow):
    """
    Identity input
    f(x) = x
    """

    def __init__(self) -> None:
        name = 'Identity'
        super().__init__(n_in_ports=1, n_out_ports=1, name=name)

    def gen_constraints(self, input_expr: Dict[int, Expr], output_expr: Dict[int, Expr]) -> List[Expr]:
        super().gen_constraints(input_expr, output_expr)
