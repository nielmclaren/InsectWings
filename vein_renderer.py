import numpy as np
import pygame
from shapely.geometry import Point, Polygon

from interveinal_region_renderer import InterveinalRegionRenderer
from param_set import ParamSet
from param_helpers import quadratic_param_to_vector2, param_to_vector2
from segment import Segment
from subdict import subdict

class VeinRenderer:
  def __init__(self, parameters:ParamSet):
    self._parameters = parameters
    self._root_segments = self._generate_segments(parameters)
    self._tip_segments = self._get_tip_segments(self._root_segments)
    self._left_interveinal_regions: list[InterveinalRegionRenderer] = []
    self._right_interveinal_regions: list[InterveinalRegionRenderer]= []

  def is_base_contained_by(self, bounds_rect:pygame.Rect, offset):
    bounds:Polygon = Polygon([
      np.subtract(bounds_rect.topleft, offset),
      np.subtract(bounds_rect.topright, offset),
      np.subtract(bounds_rect.bottomright, offset),
      np.subtract(bounds_rect.bottomleft, offset)])

    for root_segment in self._root_segments:
      if not bounds.contains(Point(root_segment.position)):
        return False

    return True

  def is_contained_by(self, bounds_rect:pygame.Rect, offset):
    bounds:Polygon = Polygon([
      np.subtract(bounds_rect.topleft, offset),
      np.subtract(bounds_rect.topright, offset),
      np.subtract(bounds_rect.bottomright, offset),
      np.subtract(bounds_rect.bottomleft, offset)])

    for root_segment in self._root_segments:
      if not bounds.contains(Point(root_segment.position)):
        return False

    for tip_segment in self._tip_segments:
      if not bounds.contains(Point(self._get_endpoint(tip_segment))):
        return False

    return True

  def has_collision(self):
    return bool(self._detect_collision(self._root_segments))

  def generate_cross_veins(self):
    self._left_interveinal_regions = self._get_interveinal_regions(self._root_segments, self._parameters)
    self._right_interveinal_regions = self._get_interveinal_regions(self._root_segments, self._parameters)

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

  def _generate_segment_and_descendants(self, parameters:ParamSet, parent_segment:Segment):
    index = parent_segment.index
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
      self._generate_segment_and_descendants(parameters, child_segment)

  def _generate_segments(self, parameters:ParamSet):
    result = []

    p = subdict(parameters, 'root_segment')

    for zero_index in range(0, parameters['num_root_segments']):
      one_index = zero_index + 1
      root_segment = Segment(
        position=quadratic_param_to_vector2(subdict(p, 'pos'), one_index),
        direction=quadratic_param_to_vector2(subdict(p, 'dir'), one_index).normalize(),
        length=p['len'],
        index=one_index)
      self._generate_segment_and_descendants(parameters, root_segment)
      result.append(root_segment)

    return result

  def _get_tip_segments(self, root_segments:list[Segment]):
    result = []
    for segment in root_segments:
      while len(segment.children) > 0:
        segment = segment.children[0]
      result.append(segment)
    return result

  def _intersection(self, seg0:Segment, seg1:Segment):
    p0:pygame.Vector2 = seg0.position
    p2:pygame.Vector2 = seg1.position
    s1:pygame.Vector2 = seg0.direction * seg0.length
    s2:pygame.Vector2 = seg1.direction * seg1.length

    denominator:float = -s2.x * s1.y + s1.x * s2.y
    if denominator == 0:
      return False

    s:float = (-s1.y * (p0.x - p2.x) + s1.x * (p0.y - p2.y)) / denominator
    t:float = ( s2.x * (p0.y - p2.y) - s2.y * (p0.x - p2.x)) / denominator

    #if s >= 0 and s <= 1 and t >= 0 and t <= 1:
    if s > 0 and s < 1 and t > 0 and t < 1:
      return pygame.Vector2(p0.x + t * s1.x, p0.y + t * s1.y)

    return False

  def _detect_collision(self, frontier:list[Segment], accumulator=False):
    if not accumulator:
      accumulator = []

    # Breadth-first search will find collisions sooner.
    next_frontier = []
    for frontier_segment in frontier:
      for segment in accumulator:
        if frontier_segment.index == segment.index and abs(frontier_segment.generation - segment.generation) < 2:
          # Ignore adjacent segments.
          continue

        x = self._intersection(frontier_segment, segment)
        if x:
          return x
      accumulator.append(frontier_segment)
      for child_segment in frontier_segment.children:
        next_frontier.append(child_segment)

    if len(next_frontier) > 0:
      return self._detect_collision(next_frontier, accumulator)
    return False

  def _get_interveinal_regions(self, root_segments: list[Segment], parameters:ParamSet) -> list[InterveinalRegionRenderer]:
    result = []
    prev_segment:Segment | None = None
    for segment in root_segments:
      if prev_segment is not None:
        result.append(InterveinalRegionRenderer(prev_segment, segment, parameters))
      prev_segment = segment
    return result

  def _render_segment_and_descendants(self, surf, offset, h_flip, index, seg):
    color = pygame.Color(255, 255, 255, self._parameters["alpha"])
    point = np.add(offset, np.multiply([h_flip, 1], seg.position))
    endpoint = np.add(offset, np.multiply([h_flip, 1], self._get_endpoint(seg)))
    pygame.draw.line(surf, color, point, endpoint, 3)

    for child_segment in seg.children:
      self._render_segment_and_descendants(surf, offset, h_flip, index, child_segment)

  def render_to(self, surf, offset):
    for interveinal_region in self._left_interveinal_regions:
      interveinal_region.render_to(surf, offset, -1)

    for interveinal_region in self._right_interveinal_regions:
      interveinal_region.render_to(surf, offset, 1)

    for index, root_segment in enumerate(self._root_segments):
      self._render_segment_and_descendants(surf, offset, -1, index, root_segment)
      self._render_segment_and_descendants(surf, offset, 1, index, root_segment)

  # TODO: De-duplicate with interveinal_region_renderer.py
  def _get_endpoint(self, segment:Segment):
    return segment.position + segment.direction * segment.length
