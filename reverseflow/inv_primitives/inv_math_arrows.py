"""Constructors for inverse arrows."""

from arrows.compositearrow import CompositeArrow
from reverseflow.util.mapping import Bimap
from arrows.primitive.math_arrows import *
from arrows.primitive.control_flow import DuplArrow
from arrows.port_attributes import *


class InvAddArrow(CompositeArrow):
    """
    Parametric Inverse Addition
    add-1(z; theta) = (z-theta, theta)
    """

    def __init__(self):
        name = "InvAdd"
        edges = Bimap()  # type: EdgeMap
        dupl_theta = DuplArrow()
        sub = SubArrow()

        in_ports = [sub.in_ports()[0], dupl_theta.in_ports()[0]]
        out_ports = [sub.out_ports()[0], dupl_theta.out_ports()[1]]
        edges.add(dupl_theta.out_ports()[0], sub.in_ports()[1])

        super().__init__(edges=edges,
                         in_ports=in_ports,
                         out_ports=out_ports,
                         name=name)
        make_param_port(self.ports()[1])

class InvSubArrow(CompositeArrow):
    """
    Parametric Inverse Subtraction
    sub-1(z; theta) = (z+theta, theta)
    """
    def __init__(self):
        name = "InvSub"
        edges = Bimap()  # type: EdgeMap
        dupl_theta = DuplArrow()
        add = AddArrow()

        in_ports = [add.in_ports()[0], dupl_theta.in_ports()[0]]
        edges.add(dupl_theta.out_ports()[0], add.in_ports()[1])
        out_ports = [add.out_ports()[0], dupl_theta.out_ports()[1]]

        super().__init__(edges=edges,
                         in_ports=in_ports,
                         out_ports=out_ports,
                         name=name)
        make_param_port(self.ports()[1])


class InvMulArrow(CompositeArrow):
    """
    Parametric Inverse Multiplication
    mul-1(z; theta) = (z/theta, theta)
    TODO: consider singularities
    """
    def __init__(self):
        name = "InvMul"
        edges = Bimap()  # type: EdgeMap
        dupl_theta = DuplArrow()
        div = DivArrow()

        in_ports = [div.in_ports()[0], dupl_theta.in_ports()[0]]
        out_ports = [div.out_ports()[0], dupl_theta.out_ports()[1]]
        edges.add(dupl_theta.out_ports()[0], div.in_ports()[1])

        super().__init__(edges=edges,
                         in_ports=in_ports,
                         out_ports=out_ports,
                         name=name)
        make_param_port(self.ports()[1])


class InvDivArrow(CompositeArrow):
    """
    Parametric Inverse Division
    div-1(z; theta) = (z * theta, theta)
    TODO: consider singularities
    """
    def __init__(self):
        name = "InvDiv"
        edges = Bimap()  # type: EdgeMap
        dupl_theta = DuplArrow()
        div = DivArrow()

        in_ports = [div.in_ports()[0], dupl_theta.in_ports()[0]]
        out_ports = [div.out_ports()[0], dupl_theta.out_ports()[1]]
        edges.add(dupl_theta.out_ports()[0], div.in_ports()[1])

        super().__init__(edges=edges,
                         in_ports=in_ports,
                         out_ports=out_ports,
                         name=name)
        make_param_port(self.ports()[1])


class InvPowArrow(CompositeArrow):
    """
    Parametric Inverse Division
    pow-1(z; theta) = (theta, log_theta(z))
    TODO: consider singularities
    """
    def __init__(self) -> None:
        name = 'InvPow'
        edges = Bimap()  # type: EdgeMap
        dupl_theta = DuplArrow()
        log = LogBaseArrow()

        in_ports = [log.in_ports()[1], dupl_theta.in_ports()[0]]
        out_ports = [dupl_theta.out_ports()[1], log.out_ports()[0]]
        edges.add(dupl_theta.out_ports()[0], log.in_ports()[0])

        super().__init__(edges=edges,
                         in_ports=in_ports,
                         out_ports=out_ports,
                         name=name)
        make_param_port(self.ports()[1])

class InvAbsArrow(CompositeArrow):
    """
    Parametric Inverse abs
    abs-1(y; theta) = theta * y, where theta = -1, 1
    """
    def __init__(self) -> None:
        name = 'InvAbs'
        edges = Bimap() # type: EdgeMap
        mul = MulArrow()

        in_ports = [mul.in_ports()[0], mul.in_ports()[1]]
        out_ports = [mul.out_ports()[0]]

        super().__init__(edges=edges,
                       in_ports=in_ports,
                       out_ports=out_ports,
                       name=name)
        make_param_port(self.ports()[1])
