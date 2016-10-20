from reverseflow.arrows.arrow import Arrow
from reverseflow.arrows.compositearrow import CompositeArrow
from reverseflow.arrows.parametricarrow import ParametricArrow
from reverseflow.arrows.port import InPort, OutPort, ParamPort
from reverseflow.util.mapping import Bimap
from reverseflow.arrows.primitive.math_arrows import AddArrow, SubArrow
from reverseflow.arrows.primitive.control_flow_arrows import DuplArrow



class InvAddArrow(CompositeArrow, ParametricArrow):
    def __init__(self):
        self.name = "InvAdd"

    def inverse_of() -> Arrow:
        return AddArrow

    def procedure(self):
        # consider having theta be something other than an InPort
        edges = Bimap()  # type: EdgeMap
        dupl_theta = DuplArrow()
        sub = SubArrow()

        in_ports = sub.in_ports[0]
        out_ports = [sub.out_ports[0], dupl_theta.out_ports[1]]
        param_ports = [dupl_theta.in_ports[0]]
        edges.add(sub.in_ports[1], dupl_theta.out_ports[0])
        inv_add = ParametricArrow(edges=edges,
                                  in_ports=in_ports,
                                  out_ports=out_ports,
                                  param_ports=param_ports)
        return inv_add
