#!./venv/bin/python3

import argparse
from dataclasses import dataclass, field
import json
from math import floor
import numpy as np
import pygame_gui.elements.ui_panel
from parameters import Parameters
import pygame
import pygame.freetype
import pygame_gui
from slider_panel import SliderPanel
from subdict import subdict

pygame.init()
pygame.freetype.init()

ANIMATION_STEPS_PER_FRAME = 30
HUD_FONT = pygame.freetype.Font("DejaVuSansMono.ttf", 12)
MAX_FPS = 60
SCREEN_WIDTH = 1600
SCREEN_HEIGHT = 900
SLIDER_PANEL_WIDTH = 350

screenshot_index = 0

# TODO: Fullscreen?

parameters:Parameters = Parameters.defaults()

@dataclass
class Segment:
  age: int = 0
  generation: int = 0
  # TODO: How to specify list[Segment] when Segment is not yet defined?
  children: list['Segment'] = field(default_factory=lambda: [])

def get_args():
  parser = argparse.ArgumentParser("./main_orthoptera.py")
  parser.add_argument("-a", "--animate", help="Record frames for an animation.", action="store_const", const=True, required=False)
  return parser.parse_args()

def generate_root_segments():
  result = []
  for _ in range(0, parameters['num_root_segments']):
    segment = Segment()
    result.append(segment)
  return result

def step_segment_and_descendants(seg):
  seg.age += 1
  for child in seg.children:
    step_segment_and_descendants(child)
  if seg.generation < parameters['max_generations'] and seg.age > 10 and not seg.children:
    seg.children.append(Segment(generation=seg.generation + 1))

def render_segment_and_descendants(surf, seg, curr_pos, curr_dir, curr_len):
  next_pos = curr_pos + curr_dir * curr_len
  next_dir = curr_dir.rotate(parameters['segment_dir_offset'])
  next_len = curr_len * parameters['segment_len_factor']

  pygame.draw.line(surf, (255, 255, 255), curr_pos, next_pos, 2)
  for child in seg.children:
    render_segment_and_descendants(surf, child, next_pos, next_dir, next_len)

def param_to_vector2(parameters, prefix):
  return pygame.Vector2(parameters[f"{prefix}_x"], parameters[f"{prefix}_y"])

def render_root_segments_and_descendants(surf):
  p = subdict(parameters, 'root_segment')
  length = p['len']
  for index, root_segment in enumerate(root_segments):
    pos = param_to_vector2(p, 'pos_quadratic') * pow(index, 2) + param_to_vector2(p, 'pos_linear') * index + param_to_vector2(p, 'pos_const')
    dir = pygame.Vector2(p['dir']).rotate(index * p['dir_offset'])
    length = p['len'] + index * p['len_factor']
    render_segment_and_descendants(surf, root_segment, pos, dir, length)

def render_hud(surf, step, fps):
  text_color = (255, 255, 255)
  hud_pos = [10, 10]
  HUD_FONT.render_to(surf, hud_pos, f"Step: {step}", text_color)

  hud_pos = [10, SCREEN_WIDTH - 10]
  text = f"FPS: {fps}"
  HUD_FONT.render_to(surf, (SCREEN_WIDTH - 10 - HUD_FONT.get_rect(text).width, 10), text, text_color)

def load_parameters():
  global parameters, slider_panel
  with open('parameters.json', 'r') as f:
    parameters = json.load(f)
    slider_panel.set_parameters(parameters)
  # TODO: Set new Parameters on the SliderPanel.
  print("Loaded parameters.json")

def save_parameters():
  with open('parameters.json', 'w') as f:
    json.dump(parameters, f, indent=2)
  print("Saved parameters.json")

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
pygame.display.set_caption("Orthoptera")
clock = pygame.time.Clock()
running = True
step = 0
dt = 0

uimanager = pygame_gui.UIManager((SCREEN_WIDTH, SCREEN_HEIGHT), theme_path="theme.json")
slider_panel = SliderPanel(
  parameters=parameters,
  relative_rect=pygame.Rect((SCREEN_WIDTH - 10 - SLIDER_PANEL_WIDTH, 25), (SLIDER_PANEL_WIDTH, SCREEN_HEIGHT - 50)),
  manager=uimanager)
slider_panel.add_slider("segment_dir_offset", "int", "Segment Direction Offset", (-20, 20), click_increment=1)
slider_panel.add_slider("segment_len_factor", "float", "Segment Length Factor", (0.2, 1.2), click_increment=0.05)
slider_panel.add_slider("root_segment_pos_const_x", "int", "Root Segment Pos Const X", (0, 1920), click_increment=120)
slider_panel.add_slider("root_segment_pos_const_y", "int", "Root Segment Pos Const Y", (0, 1080), click_increment=120)
slider_panel.add_slider("root_segment_pos_linear_x", "float", "Root Segment Pos Linear X", (-50, 50), click_increment=5)
slider_panel.add_slider("root_segment_pos_linear_y", "float", "Root Segment Pos Linear Y", (-50, 50), click_increment=5)
slider_panel.add_slider("root_segment_pos_quadratic_x", "float", "Root Segment Pos Quadratic X", (-5, 5), click_increment=0.5)
slider_panel.add_slider("root_segment_pos_quadratic_y", "float", "Root Segment Pos Quadratic Y", (-5, 5), click_increment=0.5)

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

    slider_panel.process_events(event)
    uimanager.process_events(event)

  uimanager.update(dt)

  screen.fill("black")
  screen.blit(reference_image, (-200, -300))

  for root_segment in root_segments:
    step_segment_and_descendants(root_segment)

  render_root_segments_and_descendants(screen)

  render_hud(screen, step, floor(np.average(fps_array)) if len(fps_array) else 0)
  
  uimanager.draw_ui(screen)

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