from dataclasses import dataclass, field
from decimal import Decimal
from typing import Any
@dataclass
class CustomData:
    ammo: list[tuple[Any, ...]] = field(default_factory=list)
    barrel: list[tuple[Any, ...]] = field(default_factory=list)
    laser: list[tuple[Any, ...]] = field(default_factory=list)
    magazine: list[tuple[Any, ...]] = field(default_factory=list)
    muzzle: list[tuple[Any, ...]] = field(default_factory=list)
    rear_grip: list[tuple[Any, ...]] = field(default_factory=list)
    site: list[tuple[Any, ...]] = field(default_factory=list)
    stock: list[tuple[Any, ...]] = field(default_factory=list)
    underbarrel: list[tuple[Any, ...]] = field(default_factory=list)



