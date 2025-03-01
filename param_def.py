from math import floor
from typing import Literal, Tuple

class ParamDef():
  def __init__(self, name: str, type: Literal['float', 'int'], range: Tuple['float', 'float']):
    self.name: str = name
    self.type: Literal['float', 'int'] = type

    if range[1] < range[0]:
      print(f"Warning: invalid range for {name}. {range}")
    self.range: Tuple['float', 'float'] = range

    self.step: float = 0 if range[0] == range[1] else (range[1] - range[0]) / 100
    if type == 'int':
      self.step = max(floor(self.step), 1)
    