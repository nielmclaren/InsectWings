from math import floor
from typing import Literal, Tuple

class ParamDef():
    def __init__(
            self,
            name: str,
            param_type: Literal['float', 'int'],
            param_range: Tuple['float', 'float']):
        self.name: str = name
        self.type: Literal['float', 'int'] = param_type

        if param_range[1] < param_range[0]:
            print(f"Warning: invalid range for {name}. {param_range}")
        self.range: Tuple['float', 'float'] = param_range

        self.step: float = 0
        if param_range[0] != param_range[1]:
            self.step = (param_range[1] - param_range[0]) / 100
        if param_type == 'int':
            self.step = max(floor(self.step), 1)
