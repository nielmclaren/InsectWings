from dataclasses import dataclass, field
import pygame

from param_set import ParamSet
from param_helpers import param_to_vector2
from subdict import subdict

@dataclass
class Segment:
  age: int = 0
  generation: int = 0
  children: list['Segment'] = field(default_factory=lambda: [])


class PrimaryVeins:
  def __init__(self, parameters:ParamSet):
    self._parameters = parameters
    self._root_segments = self._generate_segments(parameters)

  def _generate_segment_and_descendants(self, parameters:ParamSet, index:int, segment:Segment):
    p = subdict(parameters, 'max_generations')
    max_generations = p['quadratic'] * pow(index, 2) + p['linear'] * index + p['const']
    if segment.generation < max_generations and len(segment.children) < 1:
      child_segment = Segment(generation=segment.generation + 1)
      segment.children.append(child_segment)
      self._generate_segment_and_descendants(parameters, index, child_segment)

  def _generate_segments(self, parameters:ParamSet):
    result = []
    for index in range(0, parameters['num_root_segments']):
      root_segment = Segment()
      self._generate_segment_and_descendants(parameters, index, root_segment)
      result.append(root_segment)

    return result

  def _render_segment_and_descendants(self, parameters, surf, index, seg, curr_pos, curr_dir, curr_len):
    next_pos = curr_pos + curr_dir * curr_len
    next_dir = (
        param_to_vector2(parameters, 'root_segment_dir_quadratic') * pow(index, 2) + \
        param_to_vector2(parameters, 'root_segment_dir_linear') * index + \
        param_to_vector2(parameters, 'root_segment_dir_const') + \
        param_to_vector2(parameters, 'segment_dir_quadratic') * pow(seg.generation, 2) + \
        param_to_vector2(parameters, 'segment_dir_linear') * seg.generation + \
        param_to_vector2(parameters, 'segment_dir_a') * pow(index, 2) * pow(seg.generation, 2) + \
        param_to_vector2(parameters, 'segment_dir_b') * pow(index, 2) * seg.generation + \
        param_to_vector2(parameters, 'segment_dir_c') * index * pow(seg.generation, 2) + \
        param_to_vector2(parameters, 'segment_dir_d') * index * seg.generation
      ).normalize()
    
    next_len = curr_len * parameters['segment_len_factor']

    color = pygame.Color(255, 255, 255, parameters['alpha'])
    pygame.draw.line(surf, color, curr_pos, next_pos, 2)
    for child in seg.children:
      self._render_segment_and_descendants(parameters, surf, index, child, next_pos, next_dir, next_len)

  def render_to(self, surf):
    p = subdict(self._parameters, 'root_segment')
    length = p['len']
    for index, root_segment in enumerate(self._root_segments):
      pos = param_to_vector2(p, 'pos_quadratic') * pow(index, 2) + \
        param_to_vector2(p, 'pos_linear') * index + \
        param_to_vector2(p, 'pos_const')
      dir = (param_to_vector2(p, 'dir_quadratic') * pow(index, 2) + \
        param_to_vector2(p, 'dir_linear') * index + \
        param_to_vector2(p, 'dir_const')).normalize()
      self._render_segment_and_descendants(self._parameters, surf, index, root_segment, pos, dir, length)