"""Constructors for inverse arrows."""

from arrows.compositearrow import CompositeArrow
from reverseflow.util.mapping import Bimap
from arrows.primitive.math_arrows import *
from arrows.primitive.control_flow_arrows import DuplArrow


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

        in_ports = [sub.get_in_ports()[0], dupl_theta.get_in_ports()[0]]
        out_ports = [sub.get_out_ports()[0], dupl_theta.get_out_ports()[1]]
        edges.add(dupl_theta.get_out_ports()[0], sub.get_in_ports()[1])

        super().__init__(edges=edges,
                         in_ports=in_ports,
                         out_ports=out_ports,
                         name=name)
        self.add_in_port_attribute(1, "Param")


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

        in_ports = [add.get_in_ports()[0], dupl_theta.get_in_ports()[0]]
        edges.add(dupl_theta.get_out_ports()[0], add.get_in_ports()[1])
        out_ports = [add.get_out_ports()[0], dupl_theta.get_out_ports()[1]]

        super().__init__(edges=edges,
                         in_ports=in_ports,
                         out_ports=out_ports,
                         name=name)
        self.add_in_port_attribute(1, "Param")


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

        in_ports = [div.get_in_ports()[0], dupl_theta.get_in_ports()[0]]
        out_ports = [div.get_out_ports()[0], dupl_theta.get_out_ports()[1]]
        edges.add(dupl_theta.get_out_ports()[0], div.get_in_ports()[1])

        super().__init__(edges=edges,
                         in_ports=in_ports,
                         out_ports=out_ports,
                         name=name)
        self.add_in_port_attribute(1, "Param")


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

        in_ports = [div.get_in_ports()[0], dupl_theta.get_in_ports()[0]]
        out_ports = [div.get_out_ports()[0], dupl_theta.get_out_ports()[1]]
        edges.add(dupl_theta.get_out_ports()[0], div.get_in_ports()[1])

        super().__init__(edges=edges,
                         in_ports=in_ports,
                         out_ports=out_ports,
                         name=name)
        self.add_in_port_attribute(1, "Param")


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

        in_ports = [log.get_in_ports()[1], dupl_theta.get_in_ports()[0]]
        out_ports = [dupl_theta.get_out_ports()[1], log.get_out_ports()[0]]
        edges.add(dupl_theta.get_out_ports()[0], log.get_in_ports()[0])

        super().__init__(edges=edges,
                         in_ports=in_ports,
                         out_ports=out_ports,
                         name=name)
        self.add_in_port_attribute(1, "Param")
