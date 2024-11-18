from dataclasses import dataclass, field
from math import floor
import pygame
import random
from shapely.geometry import Polygon

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
    self._tip_segments = self._get_tip_segments(self._root_segments)
    self._first_intersection = self._detect_collision(self._root_segments)
    self._area_totals = []

  def has_collision(self):
    return self._first_intersection != False
  
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
    # TODO: Handle the case where the denominator is zero.
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
  
  def _render_segment_and_descendants(self, surf, index, seg):
    color = pygame.Color(255, 255, 255, self._alpha)
    pygame.draw.line(surf, color, seg.position, self._get_endpoint(seg), 2)
    for child_segment in seg.children:
      self._render_segment_and_descendants(surf, index, child_segment)

  def render_to(self, surf):
    for index, root_segment in enumerate(self._root_segments):
      self._render_segment_and_descendants(surf, index, root_segment)

    if self._first_intersection:
      color = pygame.Color(255, 255, 255, self._alpha)
      pygame.draw.circle(surf, color, self._first_intersection, 10, width=3)

  def _get_flood_fill_point(self, seg0:Segment, seg1:Segment):
    return (seg0.position + self._get_endpoint(seg0) + seg1.position + self._get_endpoint(seg1)) / 4

  def render_perimeter_to(self, surf):
    index = 0
    self._render_segment_and_descendants(surf, index, self._root_segments[index])
    index = len(self._root_segments) - 1
    self._render_segment_and_descendants(surf, index, self._root_segments[index])
    
    prev_segment = False
    for segment in self._root_segments:
      color = pygame.Color(255, 255, 255, self._alpha)
      if prev_segment:
        pygame.draw.line(surf, color, prev_segment.position, segment.position, 2)
      prev_segment = segment

    prev_segment = False
    for segment in self._tip_segments:
      color = pygame.Color(255, 255, 255, self._alpha)
      if prev_segment:
        pygame.draw.line(surf, color,
          self._get_endpoint(prev_segment),
          self._get_endpoint(segment), 2)
      prev_segment = segment

    self._area_totals = []
    prev_segment = False
    for segment in self._root_segments:
      if prev_segment:
        color = pygame.Color(255, 0, 0)
        pos = self._get_flood_fill_point(prev_segment, segment)
        self._area_totals.append(self._flood_fill(surf, pos, color))
      prev_segment = segment

    self._area_totals2 = []
    prev_segment = False
    for segment in self._root_segments:
      if prev_segment:
        self._area_totals2.append(self._get_area(segment, prev_segment))
      prev_segment = segment

    prev_segment = False
    for segment in self._root_segments:
      color = pygame.Color(255, 255, 255, self._alpha)
      if prev_segment:
        pygame.draw.line(surf, color, prev_segment.position, segment.position, 2)
        pos = self._get_flood_fill_point(prev_segment, segment)
        color = pygame.Color(255, 255, 255, self._alpha)
        pygame.draw.circle(surf, color, pos, 3, width=3)
      prev_segment = segment
    
    for n in self._area_totals:
      print(f"{n} ", end="")
    print()

    for n in self._area_totals2:
      print(f"{round(n)} ", end="")
    print()
 
  def _get_endpoint(self, segment:Segment):
    return segment.position + segment.direction * segment.length
  
  def _flood_fill(self, surf, position:pygame.Vector2, color:pygame.Color):
    pos = (floor(position.x), floor(position.y))
    fill_color = surf.map_rgb(color) # Convert the color to mapped integer value.
    print(f"Fill color: {fill_color} unmapped: {surf.unmap_rgb(fill_color)}")
    surf_array = pygame.surfarray.pixels2d(surf) # Create an array from the surface.
    print(f"Surf array: {len(surf_array)}x{len(surf_array[0])}")
    current_color = surf_array[pos] # Get the mapped integer color value at the fill position.
    print(f"Current color: {current_color} unmapped: {surf.unmap_rgb(current_color)}")

    if current_color == fill_color:
      return

    frontier = [pos]
    area = 0
    while len(frontier) > 0:
        x, y = frontier.pop()
        try:  # Add a try-except block in case the position is outside the surface.
            if surf_array[x, y] != current_color:
                continue
        except IndexError:
            continue
        surf_array[x, y] = fill_color
        area += 1

        # Then we append the neighbours of the pixel in the current position to our 'frontier' list.
        frontier.append((x + 1, y))  # Right.
        frontier.append((x - 1, y))  # Left.
        frontier.append((x, y + 1))  # Down.
        frontier.append((x, y - 1))  # Up.

    pygame.surfarray.blit_array(surf, surf_array)
    return area

  def _get_area(self, seg0, seg1):
    # Get a list of points traveling down seg0 and up seg1.
    points = []
    points.extend(self._get_segment_points(seg0))
    points.extend(reversed(self._get_segment_points(seg1)))
    polygon = Polygon(points)
    return polygon.area
  
  def _get_segment_points(self, segment:Segment):
    result = []
    while True:
      result.append((segment.position.x, segment.position.y))
      if len(segment.children) > 0:
        segment = segment.children[0]
      else:
        break
    endpoint = self._get_endpoint(segment)
    result.append((endpoint.x, endpoint.y))
    return result
