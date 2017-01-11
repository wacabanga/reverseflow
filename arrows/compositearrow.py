from typing import Set, Sequence, List
from arrows import Arrow
from reverseflow.util.mapping import Bimap, Relation
from arrows.port import Port, InPort, OutPort

EdgeMap = Bimap[OutPort, InPort]
RelEdgeMap = Relation[Port, Port]


def is_exposed(port: Port, context: "CompositeArrow") -> bool:
    """Is this Port exposed within this arrow, i.e. can it be connected
       to an edge.
       """
    return context == port.arrow or port.arrow.parent == context


def is_projecting(port: Port, context: "CompositeArrow") -> bool:
    """Is this port projecting in this context"""
    # assert is_exposed(port, context), "Port not expsoed in this context"
    if port.arrow == context:
        return isinstance(port, InPort)
    else:
        return isinstance(port, OutPort)


def is_receiving(port: Port, context: "CompositeArrow") -> bool:
    # A port is receiving (in some context) if it is not projecting
    return not is_projecting(port, context)


class CompositeArrow(Arrow):
    """
    Composite arrow
    A composite arrow is a composition of SubArrows
    """

    def has_in_port_type(self, PortType) -> bool:
        return any((isinstance(PortType, port) for port in self.get_in_ports()))

    def has_out_port_type(self, PortType) -> bool:
        return any((isinstance(PortType, port) for port in self.get_out_ports()))

    def neigh_in_ports(self, out_port: OutPort) -> Sequence[InPort]:
        return self.edges.fwd(out_port)

    def neigh_out_ports(self, in_port: InPort) -> Sequence[OutPort]:
        return self.edges.inv(in_port)

    def get_all_arrows(self) -> Set[Arrow]:
        """Return all arrows including self"""
        arrows = set()
        for (out_port, in_port) in self.edges.items():
            arrows.add(out_port.arrow)
            arrows.add(in_port.arrow)

        return arrows

    def get_sub_arrows(self) -> Set[Arrow]:
        """Return all the constituent arrows of composition"""
        arrows = self.get_all_arrows()
        arrows.remove(self)
        return arrows


    def is_wired_correctly(self) -> bool:
        """Is this composite arrow wired up correctly"""

        # Ensure that each left hand node is projecting and right receiving
        for left, right in self.edges.items():
            assert is_projecting(left, self), "port %s not projecting" % left
            assert is_receiving(right, self), "port %s not receiving" % right

        # Ensure no dangling ports
        out_port_fan = {}
        in_port_fan = {}
        # for sub_arrow in self.get_all_arrows():
        #     for out_port in sub_arrow.get_out_ports():
        #         out_port_fan[out_port] = 0
        #     for in_port in sub_arrow.get_in_ports():
        #         in_port_fan[in_port] = 0
        #     assert sub_arrow is not self
        #
        # for out_port, in_port in self.edges.items():
        #     out_port_fan[out_port] += 1
        #     in_port_fan[in_port] += 1
        #
        # for out_port, fan in out_port_fan.items():
        #     if not fan > 0:
        #         print("%s unused" % out_port)
        #         return False
        #
        # for in_port, fan in in_port_fan.items():
        #     if not fan == 1:
        #         print("%s has %s inp, expected 1" % (in_port, fan))
        #         return False
        #
        return True

    def num_ports(self):
        return len(self.ports)

    def are_sub_arrows_parentless(self) -> bool:
        return all((arrow.parent is None for arrow in self.get_sub_arrows()))

    def add_port_attribute(self, index: int, attribute: str):
        self.port_attributes[index].add(attribute)

    def add_in_port_attribute(self, index: int, attribute: str):
        assert index < self.num_in_ports()
        self.add_port_attribute(index, attribute)

    def add_out_port_attribute(self, index: int, attribute: str):
        assert self.num_in_ports() <= index + self.num_in_ports() < self.num_ports()
        self.add_port_attribute(index, attribute)

    def __str__(self):
        return "Comp_%s_%s" % (self.name, hex(id(self)))

    def add_edge(self, left: Port, right: Port):
        """Add an edge to the composite arrow
        Args:
            left: Projecting Port
            right: receiving Port
        """
        assert left.arrow.parent is self or left.arrow.parent is None
        assert right.arrow.parent is self or right.arrow.parent is None
        left.arrow.parent = self
        right.arrow.parent = self
        self.edges.add(left, right)
        assert self.is_wired_correctly(), "The arrow is wired incorrectly"

    def get_in_ports(self) -> List[InPort]:
        """Get InPorts of an Arrow
        Returns:
            List of InPorts"""
        return [port for port in self.ports if isinstance(port, OutPort)]

    def get_out_ports(self) -> List[OutPort]:
        """Get OutPorts of an Arrow
        Returns:
            List of OutPorts"""
        return [port for port in self.ports if isinstance(port, OutPort)]


    def __init__(self,
                 edges: RelEdgeMap=None,
                 in_ports: Sequence[InPort]=None,
                 out_ports: Sequence[OutPort]=None,
                 name: str=None,
                 parent=None,
                 port_attributes=None) -> None:
        """
        Args:
            edges: wires mapping out_ports to in_ports
            in_ports: list of out_ports of sub_arrows to be linked to in_ports of composition
            out_ports: list of out_ports of sub_arrows to be linked to out_ports of composition
            name: name of composition
            parent: Composite arrow this arrow is embedded in
            port_attributes: tags for ports
        Returns:
            Composite Arrow

        Port indices are continugous 0 ... n_ports, but types are not.
        """
        super().__init__(name=name)
        n_ports = len(in_ports) + len(out_ports)

        self.ports = []
        self.edges = Relation()
        for out_port, in_port in edges.items():
            self.edges.add(out_port, in_port)

        # InPorts are number 0, .., n, OutPorts n+1, ..., m
        out_port_0_id = len(in_ports)
        if in_ports:
            for in_port in in_ports:
                assert isinstance(in_port, InPort)
                self.ports.append(in_port)

        if out_ports:
            for out_port in out_ports:
                assert isinstance(out_port, OutPort)
                self.ports.append(out_port)

        if port_attributes is None:
            self.port_attributes = [set() for i in range(n_ports)]
        else:
            assert len(port_attributes) == n_ports
        self.ports = self.get_in_ports() + self.get_out_ports()

        # create new edges for composition
        for i, in_port in enumerate(in_ports):
            self.edges.add(self.get_in_ports()[i], in_port)

        for i, out_port in enumerate(out_ports):
            self.edges.add(out_port, self.get_out_ports()[i])

        assert self.is_wired_correctly(), "The arrow is wired incorrectly"
        assert self.are_sub_arrows_parentless(), "subarrows must be parentless"
        # Make this arrow the parent of each sub_arrow
        for sub_arrow in self.get_sub_arrows():
            sub_arrow.parent = self
