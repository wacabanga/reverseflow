from reverseflow.arrows.arrow import Arrow
from reverseflow.arrows.port import InPort, OutPort
from typing import Dict, List, MutableMapping
from sympy import Expr, Rel

class PrimitiveArrow(Arrow):
    """Primitive arrow"""
    def is_primitive(self) -> bool:
        return True

    def num_in_ports(self):
        return self.n_in_ports

    def num_out_ports(self):
        return self.n_out_ports

    def gen_constraints(self, input_expr: MutableMapping[int, Expr], output_expr: MutableMapping[int, Expr]) -> List[Rel]:
        return []

    def __init__(self, n_in_ports: int, n_out_ports: int, name: str) -> None:
        super().__init__(name=name)
        self.n_in_ports = n_in_ports
        self.n_out_ports = n_out_ports
        self.in_ports = [InPort(self, i) for i in range(n_in_ports)]
        self.out_ports = [OutPort(self, i) for i in range(n_out_ports)]
