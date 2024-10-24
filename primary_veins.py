from dataclasses import dataclass, field
import pygame

from param_set import ParamSet
from param_helpers import quadratic_param_to_vector2, param_to_vector2
from subdict import subdict

@dataclass
class Segment:
  position:pygame.Vector2
  direction:pygame.Vector2
  length:float
  age: int = 0
  index: int = 0
  generation: int = 0
  children: list['Segment'] = field(default_factory=lambda: [])


class PrimaryVeins:
  def __init__(self, parameters:ParamSet):
    self._alpha = parameters['alpha']
    self._root_segments = self._generate_segments(parameters)
    self._has_collision = self._detect_collision(self._root_segments)
  
  def _get_segment_direction(self, parameters:ParamSet, index:int, generation:int):
    return (
        param_to_vector2(parameters, 'root_segment_dir_quadratic') * pow(index, 2) + \
        param_to_vector2(parameters, 'root_segment_dir_linear') * index + \
        param_to_vector2(parameters, 'root_segment_dir_const') + \
        param_to_vector2(parameters, 'segment_dir_quadratic') * pow(generation, 2) + \
        param_to_vector2(parameters, 'segment_dir_linear') * generation + \
        param_to_vector2(parameters, 'segment_dir_a') * pow(index, 2) * pow(generation, 2) + \
        param_to_vector2(parameters, 'segment_dir_b') * pow(index, 2) * generation + \
        param_to_vector2(parameters, 'segment_dir_c') * index * pow(generation, 2) + \
        param_to_vector2(parameters, 'segment_dir_d') * index * generation
      ).normalize()

  def _generate_segment_and_descendants(self, parameters:ParamSet, index:int, parent_segment:Segment):
    p = subdict(parameters, 'max_generations')
    max_generations = p['quadratic'] * pow(index, 2) + p['linear'] * index + p['const']

    if parent_segment.generation < max_generations:
      generation = parent_segment.generation + 1
      child_segment = Segment(
        position=parent_segment.position + parent_segment.direction * parent_segment.length,
        direction=self._get_segment_direction(parameters, index, generation),
        length=parent_segment.length * parameters['segment_len_factor'],
        index=index,
        generation=generation
      )
      parent_segment.children.append(child_segment)
      self._generate_segment_and_descendants(parameters, index, child_segment)

  def _generate_segments(self, parameters:ParamSet):
    result = []

    p = subdict(parameters, 'root_segment')

    for index in range(0, parameters['num_root_segments']):
      root_segment = Segment(
        position=quadratic_param_to_vector2(subdict(p, 'pos'), index),
        direction=quadratic_param_to_vector2(subdict(p, 'dir'), index).normalize(),
        length=p['len'],
        index=index)
      self._generate_segment_and_descendants(parameters, index, root_segment)
      result.append(root_segment)

    return result

  def _detect_collision_segments(self, seg0:Segment, seg1:Segment):
    return False

  def _detect_collision(self, frontier:list[Segment], accumulator:list[Segment]=[]):
    # Breadth-first search will find collisions sooner.
    next_frontier = []
    for frontier_segment in frontier:
      for segment in accumulator:
        if self._detect_collision_segments(frontier_segment, segment):
          return True
      accumulator.append(frontier_segment)
      for child_segment in frontier_segment.children:
        next_frontier.append(child_segment)

    if len(next_frontier) > 0:
      return self._detect_collision(next_frontier, accumulator)
    return False
        
  def _render_segment_and_descendants(self, surf, index, seg):
    color = pygame.Color(255, 255, 255, self._alpha)
    pygame.draw.line(surf, color, seg.position, seg.position + seg.direction * seg.length, 2)
    for child_segment in seg.children:
      self._render_segment_and_descendants(surf, index, child_segment)

  def render_to(self, surf):
    for index, root_segment in enumerate(self._root_segments):
      self._render_segment_and_descendants(surf, index, root_segment)