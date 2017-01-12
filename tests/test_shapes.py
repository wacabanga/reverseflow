import pdb

import numpy as np
from arrows import Arrow
from arrows.apply.shapes import propagate_shapes
from reverseflow.inv_primitives.inv_math_arrows import InvAddArrow

from test_arrows import all_test_arrow_gens, test_inv_twoxyplusx
from totality_test import totality_test


def input_gen(arrow: Arrow):
    ndim = 3
    maxdim = 100
    input_shape = tuple([np.random.randint(1, maxdim) for i in range(ndim)])
    return [None if "Param" in arrow.port_attributes[i] else input_shape
            for i in range(arrow.num_in_ports())]


def test_apply():
    all_test_arrows = [gen() for gen in all_test_arrow_gens]
    totality_test(propagate_shapes, all_test_arrows, input_gen)


def manual_inspection():
    """Manually inspect output with PDB."""
    arrow = InvAddArrow()
    given_shapes = input_gen(arrow)
    output_shapes, input_shapes = propagate_shapes(arrow, given_shapes)
    pdb.set_trace()
    return shapes


if __name__ == '__main__':
    manual_inspection()
