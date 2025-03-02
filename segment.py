
from dataclasses import dataclass, field
from pygame import Vector2

@dataclass
class Segment:
    position:Vector2
    direction:Vector2
    length:float
    age: int = 0
    index: int = 0
    generation: int = 0
    children: list['Segment'] = field(default_factory=lambda: [])
