import pygame
import random
from shapely.geometry import MultiPoint, Point, Polygon
from shapely import intersection, normalize, voronoi_polygons

from param_set import ParamSet

class InterveinalRegionRenderer:
  def __init__(self, polygon, parameters:ParamSet):
    self._alpha = parameters['alpha']
    self._polygon = polygon
    self._inhibitory_centers = self._get_inhibitory_centers(self._polygon)
    self._voronoi_polygons = self._get_voronoi_polygons(self._inhibitory_centers, self._polygon)

  def render_to(self, surf):
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

  def _get_inhibitory_centers(self, interveinal_region):
    area = interveinal_region.area
    bounds = interveinal_region.bounds
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

      if not interveinal_region.contains(candidate):
        failed_attempts += 1
        continue
      # TODO: Might need to use a line string here.

      # if interveinal_region.dwithin(candidate, min_distance):
      #   failed_attempts += 1
      #   continue

      if multi_point.dwithin(candidate, min_distance):
        failed_attempts += 1
        continue

      multi_point = MultiPoint(list(multi_point.geoms) + [candidate])
      failed_attempts = 0
    return multi_point

  def _get_voronoi_polygons(self, inhibitory_centers, extent):
    return intersection(normalize(voronoi_polygons(inhibitory_centers, extend_to=extent)).geoms, extent)
