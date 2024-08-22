#!/usr/bin/python3

import argparse
import dataclasses
from dataclasses import dataclass, field
import json
from math import floor
import numpy as np
import pygame
import pygame.freetype
from typing import TypedDict

# Reaction-Diffusion algorithm adapted from Reddit user Doormatty.
# https://www.reddit.com/r/Python/comments/og8vh6/comment/h4k2408/?utm_source=share&utm_medium=web3x&utm_name=web3xcss&utm_term=1&utm_content=share_button

pygame.init()
pygame.freetype.init()

ANIMATION_STEPS_PER_FRAME = 30
HUD_FONT = pygame.freetype.Font("DejaVuSansMono.ttf", 12)
MAX_FPS = 60
SCREEN_WIDTH = 1600
SCREEN_HEIGHT = 900

screenshot_index = 0

# TODO: Fullscreen?

class Parameters(TypedDict):
  num_root_segments: int
  root_segment_len: float
  root_segment_dir_x: float
  root_segment_dir_y: float
parameters = Parameters(
  num_root_segments=12,
  root_segment_len=100,
  root_segment_dir_x=1,
  root_segment_dir_y=-0.1,
)

@dataclass
class Segment:
  age: int = 0
  generation: int = 0
  dir: pygame.Vector2 = (0, 0)
  len: float = 0.0
  # TODO: How to specify list[Segment] when Segment is not yet defined?
  children: list['Segment'] = field(default_factory=lambda: [])

@dataclass
class RootSegment(Segment):
  pos: pygame.Vector2 = (0, 0)

def get_args():
  parser = argparse.ArgumentParser("./main_lsys.py")
  parser.add_argument("-a", "--animate", help="Record frames for an animation.", action="store_const", const=True, required=False)
  return parser.parse_args()

def generate_root_segments():
  pos = pygame.Vector2(295, 340)
  dir = pygame.Vector2(parameters['root_segment_dir_x'], parameters['root_segment_dir_y'])

  result = []
  for _ in range(0, parameters['num_root_segments']):
    segment = RootSegment(pos=pos, dir=dir, len=parameters['root_segment_len'])
    result.append(segment)
    pos = pos + (-5, 10)
    dir = dir.rotate(4)
  return result

def step_segment_and_descendants(seg):
  seg.age += 1
  for child in seg.children:
    step_segment_and_descendants(child)
  if seg.generation < 12 and seg.age > 10 and not seg.children:
    seg.children.append(Segment(generation=seg.generation + 1, dir=seg.dir.rotate(2), len=seg.len * 0.95))

def render_segment_and_descendants(seg, base_pos):
  next_pos = base_pos + seg.dir * seg.len
  pygame.draw.line(screen, (255, 255, 255), base_pos, next_pos, 2)
  for child in seg.children:
    render_segment_and_descendants(child, next_pos)

def render_hud_to(surf, step, fps):
  text_color = (255, 255, 255)
  hud_pos = [10, 10]
  HUD_FONT.render_to(surf, hud_pos, f"Step: {step}", text_color)

  hud_pos = [10, SCREEN_WIDTH - 10]
  text = f"FPS: {fps}"
  HUD_FONT.render_to(surf, (SCREEN_WIDTH - 10 - HUD_FONT.get_rect(text).width, 10), text, text_color)

def load_parameters():
  global parameters
  with open('parameters.json', 'r') as f:
    parameters = json.load(f)
  print("Loaded parameters.json")
  print(json.dumps(parameters))

def save_parameters():
  with open('parameters.json', 'w') as f:
    json.dump(parameters, f)
  print("Saved parameters.json")

def save_screenshot(surf, index):
  filename = f"output/lsys_{str(index).zfill(3)}.png"
  pygame.image.save(surf, f"{filename}")
  print(f"Saved {filename}")

def save_animation_frame(surf, frame_index):
  filename = f"output/frame_{str(frame_index).zfill(4)}.png"
  pygame.image.save(surf, f"{filename}")
  print(f"Saved {filename}")

args = get_args()

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("L-System")
clock = pygame.time.Clock()
running = True
step = 0
dt = 0
reference_image = pygame.image.load('assets/orthoptera_dark.png')
reference_image = pygame.transform.scale_by(reference_image, 4)
root_segments = generate_root_segments()
fps_array = []
animation_steps = 0
animation_frame_index = 0

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
      elif event.key == pygame.K_v:
        save_parameters()
      elif event.key == pygame.K_l:
        load_parameters()
        root_segments = generate_root_segments()
        step = 0
        animation_steps = 0

  screen.fill("black")
  screen.blit(reference_image, (-200, -300))
  for root_segment in root_segments:
    step_segment_and_descendants(root_segment)

  for root_segment in root_segments:
    render_segment_and_descendants(root_segment, root_segment.pos)

  render_hud_to(screen, step, floor(np.average(fps_array)) if len(fps_array) else 0)

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