"""Major classes for Arrow data structures"""


class Arrow:
    """Abstract arrow class"""

    def __init__(self, name: str) -> None:
        self.name = name

    def num_in_ports(self):
        return len(self.in_ports)

    def num_out_ports(self):
        return len(self.out_ports)

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

    def inner_in_ports(self):
        if self.is_composite():
            return self._inner_in_ports
        else:
            return self.in_ports

    def inner_out_ports(self):
        if self.is_composite():
            return self._inner_out_ports
        else:
            return self.out_ports
