from dataclasses import dataclass, field
from math import floor
import pygame
import random
from shapely.geometry import MultiPoint, Point, Polygon
from shapely import intersection, normalize, voronoi_polygons

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
    self._inhibitory_centers = self._get_all_inhibitory_centers(self._root_segments)
    self._voronoi_polygons = self._get_all_voronoi_polygons(self._inhibitory_centers, self._root_segments)

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
      # TODO: Remove the following break when you're finished testing using only the first region.
      if index > 0:
        break

    color = pygame.Color(255, 255, 255, self._alpha)
    if self._first_intersection:
      pygame.draw.circle(surf, color, self._first_intersection, 10, width=3)

    color = pygame.Color(255, 255, 255)
    for p in self._inhibitory_centers.geoms:
      pygame.draw.circle(surf, color, (p.x, p.y), 2, width=0)

    color = pygame.Color(255, 255, 255)
    for polygon in self._voronoi_polygons:
      points = tuple(polygon.exterior.coords)
      prev_point = False
      for point in points:
        if prev_point:
          pygame.draw.line(surf, color, prev_point, point)
        prev_point = point

  def render_perimeter_to(self, surf):
    prev_segment = False
    for segment in self._root_segments:
      color = pygame.Color(255, 255, 255, self._alpha)
      if prev_segment:
        pygame.draw.line(surf, color, prev_segment.position, segment.position, 2)
        # TODO: Remove the following break when you're finished testing using only the first region.
        break
      prev_segment = segment

    prev_segment = False
    for segment in self._tip_segments:
      color = pygame.Color(255, 255, 255, self._alpha)
      if prev_segment:
        pygame.draw.line(surf, color,
          self._get_endpoint(prev_segment),
          self._get_endpoint(segment), 2)
        # TODO: Remove the following break when you're finished testing using only the first region.
        break
      prev_segment = segment

  def _get_endpoint(self, segment:Segment):
    return segment.position + segment.direction * segment.length

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

  def _get_all_inhibitory_centers(self, root_segments):
    result = []
    prev_segment = False
    for segment in root_segments:
      if prev_segment:
        result.extend(self._get_inhibitory_centers(prev_segment, segment))
        # TODO: Remove the following break when you're finished testing using only the first region.
        break
      prev_segment = segment
    return MultiPoint(result)

  def _get_inhibitory_centers(self, seg0, seg1):
    polygon = self._get_polygon(seg0, seg1)
    area = polygon.area
    bounds = polygon.bounds
    min_distance = 30

    print(f"Area: {area}")

    max_failed_attempts = 100
    failed_attempts = 0
    max_results = 100 # TODO Scale this based on the area.
    multi_point = MultiPoint([])
    while len(multi_point.geoms) < max_results:
      if failed_attempts >= max_failed_attempts:
        print(f"Max failed attempts reached. num_points={len(multi_point.geoms)}")
        break

      candidate = Point(random.uniform(bounds[0], bounds[2]), random.uniform(bounds[1], bounds[3]))

      if not polygon.contains(candidate):
        failed_attempts += 1
        continue
      # TODO: Might need to use a line string here.

      # if polygon.dwithin(candidate, min_distance):
      #   failed_attempts += 1
      #   continue

      if multi_point.dwithin(candidate, min_distance):
        failed_attempts += 1
        continue

      multi_point = MultiPoint(list(multi_point.geoms) + [candidate])
      failed_attempts = 0
    return map(lambda p: (p.x, p.y), list(multi_point.geoms))

  def _get_all_voronoi_polygons(self, inhibitory_centers, root_segments):
    result = []
    prev_segment = False
    for segment in root_segments:
      if prev_segment:
        interveinal_region = self._get_polygon(prev_segment, segment)
        result.extend(self._get_voronoi_polygons(inhibitory_centers, interveinal_region))
        # TODO: Remove the following break when you're finished testing using only the first region.
        break
      prev_segment = segment
    return result

  def _get_voronoi_polygons(self, inhibitory_centers, extent):
    return intersection(normalize(voronoi_polygons(inhibitory_centers, extend_to=extent)).geoms, extent)

  def _get_polygon(self, seg0, seg1):
    # Get a list of points traveling down seg0 and up seg1.
    points = []
    points.extend(self._get_segment_points(seg0))
    points.extend(reversed(self._get_segment_points(seg1)))
    return Polygon(points)
