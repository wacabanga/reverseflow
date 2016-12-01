from typing import Set, List
from reverseflow.arrows.arrow import Arrow
from reverseflow.util.mapping import Bimap
from reverseflow.arrows.port import InPort, OutPort, ErrorPort, ParamPort

EdgeMap = Bimap[OutPort, InPort]


class CompositeArrow(Arrow):
    """
    Composite arrow
    A composite arrow is a composition of arrows, which may be either
    primtive arrows or themselves compositions.
    """

    def is_composite(self) -> bool:
        return True

    def is_parametric(self) -> bool:
        return len(self.param_ports) > 0

    def is_approximate(self) -> bool:
        return len(self.error_ports) > 0

    def get_sub_arrows(self) -> Set[Arrow]:
        """Return all the constituent arrows of composition"""
        arrows = set()
        for (out_port, in_port) in self.edges.items():
            arrows.add(out_port.arrow)
            arrows.add(in_port.arrow)

        return arrows

    def __init__(self,
                 edges: EdgeMap,
                 in_ports: List[InPort],
                 out_ports: List[OutPort],
                 param_ports: List[ParamPort] = [],
                 error_ports: List[ErrorPort] = [],
                 name: str=None) -> None:
        super().__init__(name=name)
        assert len(in_ports) > 0, "Composite Arrow must have in ports"
        assert len(out_ports) > 0, "Composite Arrow must have out ports"
        self.edges = edges
        for out_port, in_port in edges.items():
            assert isinstance(out_port, OutPort), "Expected OutPort got %s" % out_port
            assert isinstance(in_port, InPort), "Expected InPort got %s" % in_port

        arrows = self.get_sub_arrows()
        for in_port in in_ports:
            assert in_port not in edges.values(), "in_port must be unconnected"  % in_port.arrow
            assert in_port.arrow in arrows, "InPort arrow (%s) not in composition" % in_port.arrow

        for out_port in out_ports:
            assert out_port.arrow in arrows, "OutPort arrow (%s) not in composition" % out_port.arrow
            assert out_port not in edges.keys(), "out_port must be unconnected"

        # TODO: Assert There must be no cycles
        # TODO: Assert Every inport must be on end of edge or be in in_ports
        # TODO: Assert Every outport must be on start of edge or in out_ports
        self.in_ports = [InPort(self, i) for i in range(len(in_ports))]
        self.n_in_ports = len(self.in_ports)
        self.out_ports = [OutPort(self, i) for i in range(len(out_ports))]
        self.n_out_ports = len(self.out_ports)
        self.error_ports = [ErrorPort(self, i) for i in range(len(error_ports))]
        self.n_error_ports = len(self.error_ports)
        self.param_ports = [ParamPort(self, i) for i in range(len(param_ports))]
        self.n_param_ports = len(self.param_ports)
        self._inner_in_ports = in_ports  # type: List[InPort]
        self._inner_out_ports = out_ports  # type: List[OutPort]
        self._inner_param_ports = param_ports  # type: List[ParamPort]
        self._inner_error_ports = error_ports  # type: List[ErrorPort]

    def neigh_in_port(self, out_port: OutPort) -> InPort:
        return self.edges.fwd(out_port)

    def neigh_out_port(self, in_port: InPort) -> OutPort:
        return self.edges.inv(in_port)

    def inner_in_ports(self) -> List[InPort]:
        return self._inner_in_ports

    def inner_out_ports(self) -> List[OutPort]:
        return self._inner_out_ports

    def inner_error_ports(self) -> List[ErrorPort]:
        return self._inner_error_ports

    def inner_param_ports(self) -> List[ParamPort]:
        return self._inner_param_ports
