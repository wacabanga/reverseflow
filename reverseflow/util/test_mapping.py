"""Test Mapping Functions"""
from reverseflow.util.mapping import Bimap


def test_bimap():
    a = Bimap()  # type: Bimap[str, int]
    a.add("myage", 99)
    assert a.fwd("myage") == 99
    assert a.inv(99) == "myage"
