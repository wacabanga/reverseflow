"""Decode an arrow into a tensoflow graph"""
import tensorflow as tf
from tensorflow import Tensor, Graph, Variable
from pqdict import pqdict
from reverseflow.arrows.arrow import Arrow
from reverseflow.arrows.compositearrow import CompositeArrow, EdgeMap
from reverseflow.arrows.primitive.math_arrows import *
from reverseflow.arrows.primitive.control_flow_arrows import *
from reverseflow.arrows.primitive.cast_arrows import *
from reverseflow.arrows.primitive.constant import *
from reverseflow.util.misc import same
from typing import Tuple, List, Dict, MutableMapping, Union, Sequence
from collections import OrderedDict
from overloading import overload
from reverseflow.arrows.apply.interpret import interpret

ShapeList = Sequence[Tuple[int, ...]]

def same_to_n(shapes, n=1):
    assert same(shapes), "Shapes must be the same"
    return [shapes[0] for i in range(n)]

@overload
def conv(a: Arrow, shapes: ShapeList) -> ShapeList:
    assert False, "Error, no conversion for %s implemented" % a.name


@overload
def conv(a: AddArrow, shapes: ShapeList) -> ShapeList:
    return same_to_n(shapes)


@overload
def conv(a: SubArrow, shapes: ShapeList) -> ShapeList:
    return same_to_n(shapes)


@overload
def conv(a: NegArrow, shapes: ShapeList) -> ShapeList:
    return same_to_n(shapes)


@overload
def conv(a: PowArrow, shapes: ShapeList) -> ShapeList:
    return same_to_n(shapes)


@overload
def conv(a: ExpArrow, shapes: ShapeList) -> ShapeList:
    return same_to_n(shapes)


@overload
def conv(a: LogArrow, shapes: ShapeList) -> ShapeList:
    return same_to_n(shapes)


@overload
def conv(a: LogBaseArrow, shapes: ShapeList) -> ShapeList:
    # Tensorflow has no log of arbitrary base
    # so, use log _{b}(x)=log _{k}(x)}/log _{k}(b)
    return same_to_n(shapes)


@overload
def conv(a: MulArrow, shapes: ShapeList) -> ShapeList:
    return same_to_n(shapes)


@overload
def conv(a: DivArrow, shapes: ShapeList) -> ShapeList:
    return same_to_n(shapes)


@overload
def conv(a: DuplArrow, shapes: ShapeList) -> ShapeList:
    # TODO: Genralize to n outputs
    return same_to_n(shapes.n_out_ports)

@overload
def conv(a: AddNArrow, shapes: ShapeList) -> ShapeList:
    return same_to_n(shapes)

@overload
def conv(a: CastArrow, shapes: ShapeList) -> ShapeList:
    return same_to_n(shapes)

@overload
def conv(a: AbsArrow, shapes: ShapeList) -> ShapeList:
    return same_to_n(shapes)

@overload
def conv(a: RankArrow, shapes: ShapeList) -> ShapeList:
    return [()]

@overload
def conv(a: RangeArrow, shapes: ShapeList) -> ShapeList:
    assert False

@overload
def conv(a: ReduceMeanArrow, shapes: ShapeList) -> ShapeList:
    assert False


@overload
def conv(a: CompositeArrow, args: ShapeList) -> ShapeList:
    assert len(args) == a.n_in_ports
    arrow_colors, arrow_tensors = inner_convert(a, args)
    result = arrow_to_graph(a,
                            args,
                            arrow_colors,
                            arrow_tensors,
                            graph)
    return result['output_tensors']

def propagate_shapes(comp_arrow: CompositeArrow,
                     input_shapes: ShapeList):
    return interpret(conv, comp_arrow, input_shapes)
