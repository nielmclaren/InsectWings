import numpy as np
import pygame
import random
from shapely.geometry import MultiPoint, Point, Polygon
from shapely import intersection, normalize, voronoi_polygons

from param_set import ParamSet
from segment import Segment

class InterveinalRegionRenderer:
  def __init__(self, root_segment0, root_segment1, parameters:ParamSet):
    self._parameters = parameters
    self._root_segment0 = root_segment0
    self._root_segment1 = root_segment1
    self._polygon = self._get_polygon(root_segment0, root_segment1)
    inhibitory_centers = self._get_inhibitory_centers(self._polygon)
    self._inhibitory_centers = self._lloyds_algorithm(inhibitory_centers, 50)
    # self._voronoi_polygons = self._get_voronoi_polygons(self._inhibitory_centers, self._polygon)

  def render_to(self, surf, offset, h_flip):
    color = pygame.Color(255, 255, 255)
    for point in self._inhibitory_centers.geoms:
      point = (point.x, point.y)
      pygame.draw.circle(surf, color, tuple(np.add(offset, np.multiply([h_flip, 1], point))), 3)
    # for polygon in self._voronoi_polygons:
    #   points = tuple(polygon.exterior.coords)
    #   points = [tuple(np.add(offset, np.multiply([h_flip, 1], point))) for point in points]
    #   prev_point = False
    #   for point in points:
    #     if prev_point:
    #       pygame.draw.line(surf, color, prev_point, point)
    #     prev_point = point

  def _get_polygon(self, seg0, seg1):
    # Get a list of points traveling down seg0 and up seg1.
    points = []
    points.extend(self._get_segment_points(seg0))
    points.extend(reversed(self._get_segment_points(seg1)))
    return Polygon(points)

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

  # TODO: De-duplicate with vein_renderer.py
  def _get_endpoint(self, segment:Segment):
    return segment.position + segment.direction * segment.length

  def _get_inhibitory_centers(self, interveinal_region):
    area = interveinal_region.area
    bounds = interveinal_region.bounds







    min_distance = 30

    max_failed_attempts = 100
    failed_attempts = 0
    max_results = 100 # TODO Scale this based on the area.
    multi_point = MultiPoint([])
    while len(multi_point.geoms) < max_results:
      if failed_attempts >= max_failed_attempts:
        print(f"Max failed attempts reached. num_points={len(multi_point.geoms)}, area={area}, num_points/area={len(multi_point.geoms)/area}")
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
    polygons = normalize(voronoi_polygons(inhibitory_centers, extend_to=extent))
    return intersection(polygons.geoms, extent)

  def _lloyds_algorithm(self, initial_inhibitory_centers:MultiPoint, iterations:int):
    return initial_inhibitory_centers

    # inhibitory_centers = initial_inhibitory_centers
    # for _ in range(iterations):
    #   voronoi_polygons = self._get_voronoi_polygons(inhibitory_centers, self._polygon)
    #   centroids = []
    #   for polygon in voronoi_polygons:
    #     centroids.append(polygon.centroid)
    #   inhibitory_centers = MultiPoint(centroids)
    # return inhibitory_centers

