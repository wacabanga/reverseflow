import sympy

from reverseflow.arrows.apply.symbolic import symbolic_apply
from reverseflow.arrows.arrow import Arrow
from reverseflow.arrows.port import InPort, ParamPort

from util import random_arrow_test
from test_arrows import test_xyplusx_flat, all_composites


def test_symbolic_apply() -> None:
    """f(x,y) = x * y + x"""
    arrow = test_xyplusx_flat()
    input_symbols = generate_input(arrow)
    output_symbols, constraints = symbolic_apply(input_symbols)

def generate_input(arrow: Arrow):
    input_symbols = []
    for i, in_port in enumerate(arrow.in_ports):
        if isinstance(in_port, ParamPort):
            input_symbols.append(sympy.Dummy("input_%s" % i))
        elif isinstance(in_port, InPort):
            input_symbols.append(sympy.Dummy("param_%s" % i))
        else:
            assert False, "Don't know how to handle %s" % in_port
    return input_symbols

def reset_and_conv(arrow: Arrow) -> None:
    input_symbols = generate_input(arrow)
    output_symbols, constraints = symbolic_apply(input_symbols)

random_arrow_test(reset_and_conv, "to_symbolic_apply")
