"""The instruments you can pick from.

The free sound bank has no real Arabic instruments, so most of these use
the closest sound it does have. `stand_in` says which one. We'll swap in
real oud, qanun, ney and mijwiz recordings later.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class Instrument:
    name: str
    bank: int
    preset: int
    stand_in: str = ""


INSTRUMENTS = [
    Instrument("Piano", 0, 0),
    Instrument("Oud", 0, 24, "nylon guitar"),
    Instrument("Qanun", 0, 46, "harp"),
    Instrument("Buzuq", 0, 104, "sitar"),
    Instrument("Ney", 0, 77, "shakuhachi"),
    Instrument("Mijwiz", 0, 111, "shenai"),
    Instrument("Violin", 0, 40),
    Instrument("Strings", 0, 48),
    Instrument("Accordion", 0, 21),
]
