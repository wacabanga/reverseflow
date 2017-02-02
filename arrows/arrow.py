"""Major classes for Arrow data structures"""

import arrows.port_attributes as pa

class Arrow:
    """Abstract arrow class"""

    def __init__(self, name: str, parent=None) -> None:
        self.name = name
        self.parent = parent

    def get_port_attributes(self, port):
        assert port.arrow is self
        return self.port_attributes[port.index]

    def get_ports(self):
        return self._ports

    def get_port(self, index: int):
        return self.get_ports()[index]

    def get_in_ports(self):
        """
        Get InPorts of an Arrow.
        Returns:
            List of InPorts
        """
        return [port for port in self._ports if pa.is_in_port(port)]

    def get_in_port(self, index: int):
        """
        Get ith InPort
        """
        return self.get_in_ports()[index]

    def get_param_ports(self):
        """
        Get ParamPorts of an Arrow.
        Returns:
            List of ParamPorts
        """
        return [port for port in self._ports if pa.is_param_port(port)]

    def get_out_ports(self):
        """
        Get OutPorts of an Arrow.
        Returns:
            List of OutPorts
        """
        return [port for port in self._ports if pa.is_out_port(port)]

    def get_out_port(self, index: int):
        """
        Get ith OutPort
        """
        return self.get_out_ports()[index]

    def num_ports(self) -> int:
        return len(self.get_ports())

    def num_in_ports(self) -> int:
        return len(self.get_in_ports())

    def num_out_ports(self) -> int:
        return len(self.get_out_ports())

    def num_param_ports(self) -> int:
        return len(self.get_param_ports())

    def is_primitive(self) -> bool:
        return False

    def is_composite(self) -> bool:
        return False

    def is_source(self) -> bool:
        return False

    def is_parametric(self) -> bool:
        return False

    def is_approximate(self) -> bool:
        return False

    def is_tf(self) -> bool:
        return False

    def get_sub_arrows(self):
        return []

    def __deepcopy__(self, memo):
        return None
