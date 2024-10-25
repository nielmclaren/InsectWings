#!./venv/bin/python3

import argparse
from math import floor
import numpy as np
import pygame
import pygame.freetype
from subdict import subdict
from typing import Dict

pygame.init()
pygame.freetype.init()

ANIMATION_STEPS_PER_FRAME = 30
HUD_FONT = pygame.freetype.Font("DejaVuSansMono.ttf", 12)
MAX_FPS = 60
SCREEN_WIDTH = 1600
SCREEN_HEIGHT = 900
SLIDER_PANEL_WIDTH = 350

points = {
  # line segment from a to b
  'a': pygame.Vector2(200, 200),
  'b': pygame.Vector2(800, 700),

  # line segment from c to d
  'c': pygame.Vector2(300, 700),
  'd': pygame.Vector2(1200, 100)
}
dragging_point_name = False

step = 0
animation_steps = 0
animation_frame_index = 0
screenshot_index = 0

def get_args():
  parser = argparse.ArgumentParser("./main_collision_test.py")
  parser.add_argument("-a", "--animate", help="Record frames for an animation.", action="store_const", const=True, required=False)
  return parser.parse_args()

def get_nearest_point(target:pygame.Vector2):
  nearest_point_name = False
  nearest_dist = float("inf")
  for point_name, point in points.items():
    dist = (target - point).magnitude()
    if dist < nearest_dist:
      nearest_point_name = point_name
      nearest_dist = dist
  return nearest_point_name

def intersection(p0, s1, p2, s2):
  # p0:pygame.Vector2 = seg0.position
  # p2:pygame.Vector2 = seg1.position
  # s1:pygame.Vector2 = seg0.direction * seg0.length
  # s2:pygame.Vector2 = seg1.direction * seg1.length

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

def render(surf):
  global points
  a = points['a']
  b = points['b']
  c = points['c']
  d = points['d']

  print(a, b, c, d)

  x = intersection(a, b-a, c, d-c)

  color = pygame.Color(255, 0, 0) if x else pygame.Color(255, 255, 255)
  pygame.draw.line(surf, color, a, b, 2)
  pygame.draw.line(surf, color, c, d, 2)

  if x:
    pygame.draw.circle(surf, color, x, 20)

def render_hud(surf, step, fps):
  text_color = (255, 255, 255)
  hud_pos = [10, 10]
  HUD_FONT.render_to(surf, hud_pos, f"Step: {step}", text_color)

  hud_pos = [10, SCREEN_WIDTH - 10]
  text = f"FPS: {fps}"
  HUD_FONT.render_to(surf, (SCREEN_WIDTH - 10 - HUD_FONT.get_rect(text).width, 10), text, text_color)

def save_screenshot(surf, index):
  filename = f"output/orthoptera_{str(index).zfill(3)}.png"
  pygame.image.save(surf, f"{filename}")
  print(f"Saved {filename}")

def save_animation_frame(surf, frame_index):
  filename = f"output/frame_{str(frame_index).zfill(4)}.png"
  pygame.image.save(surf, f"{filename}")
  print(f"Saved {filename}")

args = get_args()

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Collision Test")
clock = pygame.time.Clock()
running = True
dt = 0

fps_array = []

while running:
  for event in pygame.event.get():
    if event.type == pygame.QUIT:
      running = False
    elif event.type == pygame.KEYDOWN:
      if event.key == pygame.K_ESCAPE:
        running = False
      elif event.key == pygame.K_r:
        save_screenshot(screen, screenshot_index)
        screenshot_index += 1
    elif event.type == pygame.MOUSEBUTTONDOWN:
      pos = pygame.mouse.get_pos()
      dragging_point_name = get_nearest_point(pos)
      print(f"Dragging {dragging_point_name}")
    elif event.type == pygame.MOUSEBUTTONUP:
      dragging_point_name = False

  if dragging_point_name:
    print(f"Assign {dragging_point_name} = {pygame.mouse.get_pos()}")
    points[dragging_point_name] = pygame.Vector2(pygame.mouse.get_pos())

  screen.fill("black")
  render(screen)

  render_hud(screen, step, floor(np.average(fps_array)) if len(fps_array) else 0)

  pygame.display.flip()

  dt = clock.tick(MAX_FPS) / 1000

  fps_array.append(1 / dt)
  fps_array = fps_array[:10]

  if args.animate and animation_steps >= ANIMATION_STEPS_PER_FRAME:
    save_animation_frame(screen, animation_frame_index)
    animation_frame_index += 1
    animation_steps = 0
  
  step += 1
  animation_steps += 1

pygame.quit()