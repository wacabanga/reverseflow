"""Propagate constants through graph"""
from arrows.port import Port
from arrows.port_attributes import PortAttributes
from enum import Enum
from arrows.port_attributes import extract_attribute, ports_has

class ValueType(Enum):
    CONSTANT = 0
    VARIABLE = 1

CONST = ValueType.CONSTANT
VAR = ValueType.VARIABLE

def constant_pred(arr, port_attr: PortAttributes):
    return ports_has(arr.in_ports(), 'constant', port_attr)


def constant_dispatch(arr, port_attr: PortAttributes, state=None):
    ptc = extract_attribute('constant', port_attr)
    # All the outputs are constant if and only if all the inputs are constant
    if all((value == CONST for value in ptc.values())):
        return {port: {'constant': CONST} for port in arr.ports()}
    else:
        return {port: {'constant': ptc[port]} if port in ptc \
    else {'constant': VAR} for port in arr.ports()}

def is_constant(p: Port, pv: PortAttributes):
    return p in pv and 'constant' in pv[p] and pv[p]['constant'] == CONST
