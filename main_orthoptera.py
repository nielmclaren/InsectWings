#!./venv/bin/python3

import json
from math import floor
import numpy as np
import pygame_gui.elements.ui_panel
import pygame
import pygame.freetype
import pygame_gui
import random
from shapely.errors import GEOSException
from typing import Dict

from get_param_defs import get_param_defs
from param_def import ParamDef
from param_set import ParamSet
from vein_renderer import VeinRenderer
from slider_panel import SliderPanel

pygame.init()
pygame.freetype.init()

HUD_FONT = pygame.freetype.Font("DejaVuSansMono.ttf", 12)
MAX_FPS = 60
SCREEN_WIDTH = 1600
SCREEN_HEIGHT = 900
SLIDER_PANEL_WIDTH = 350

TARGET_BOX = pygame.Rect((SCREEN_WIDTH/2, 20), (SCREEN_WIDTH/2 - 20, SCREEN_HEIGHT - 40))
BASE_TARGET_BOX = pygame.Rect(
  (SCREEN_WIDTH/2, SCREEN_HEIGHT * 0.2),
  (200, SCREEN_HEIGHT * 0.6))
RENDER_OFFSET = (SCREEN_WIDTH/2, 0)

EDIT_MODE = "edit_mode"
PREVIEW_MODE = "preview_mode"

export_index = 0
screenshot_index = 0

param_defs:Dict[str, ParamDef] = get_param_defs()
parameters:ParamSet = ParamSet.defaults()
vein_renderer:VeinRenderer

mode = EDIT_MODE

def render_hud(surf, fps):
  text_color = (255, 255, 255)
  text = f"FPS: {fps}"
  HUD_FONT.render_to(surf, (SCREEN_WIDTH - 10 - HUD_FONT.get_rect(text).width, 10), text, text_color)

def parameters_changed(vein_renderer_invalid:bool=True):
  global screen, vein_renderer

  if vein_renderer_invalid:
    vein_renderer = VeinRenderer(parameters)
  slider_panel.set_parameters(parameters)

def load_parameters():
  global parameters, slider_panel
  with open('parameters.json', 'r') as f:
    parameters = json.load(f)
    parameters_changed()
  print("Loaded parameters.json")

def save_parameters():
  with open('parameters.json', 'w') as f:
    json.dump(parameters, f, indent=2)
  print("Saved parameters.json")

def randomize_parameter(name:str):
  global param_defs, parameters
  param_def = param_defs[name]
  parameters[name] = random.uniform(param_def.range[0], param_def.range[1])

def randomize_base_parameters():
  global parameters
  param_names = [
    "root_segment_pos_linear_x",
    "root_segment_pos_linear_y",
    "root_segment_pos_quadratic_x",
    "root_segment_pos_quadratic_y",
  ]
  attempts_remaining = 1000
  while True:
    attempts_remaining -= 1
    if attempts_remaining < 0:
      print("Max attempts reached.")
      break
    for name in param_names:
      randomize_parameter(name)
    try:
      vein_renderer = VeinRenderer(parameters)
      if not vein_renderer.is_base_contained_by(BASE_TARGET_BOX, RENDER_OFFSET):
        print("Rejected wing base out of bounds.")
      else:
        print("Approved!")
        break

    except GEOSException:
      print("GEOSException")
  parameters_changed(False)

def randomize_primary_vein_parameters():
  global parameters
  param_names = [
    "root_segment_dir_const_x",
    "root_segment_dir_const_y",
    "root_segment_dir_linear_x",
    "root_segment_dir_linear_y",
    "root_segment_dir_quadratic_x",
    "root_segment_dir_quadratic_y",

    "segment_dir_linear_x",
    "segment_dir_linear_y",
    "segment_dir_quadratic_x",
    "segment_dir_quadratic_y",
    "segment_dir_a_x",
    "segment_dir_a_y",
    "segment_dir_b_x",
    "segment_dir_b_y",
    "segment_dir_c_x",
    "segment_dir_c_y",
    "segment_dir_d_x",
    "segment_dir_d_y"
  ]
  attempts_remaining = 1000
  while True:
    attempts_remaining -= 1
    if attempts_remaining < 0:
      print("Max attempts reached.")
      break
    for name in param_names:
      randomize_parameter(name)
    try:
      vein_renderer = VeinRenderer(parameters)
      if not vein_renderer.is_contained_by(TARGET_BOX, RENDER_OFFSET):
        print("Rejected wing out of bounds.")
      elif vein_renderer.has_collision():
        print("Rejected overlapping primary veins.")
      else:
        print("Approved!")
        parameters_changed(False)
        break

    except GEOSException:
      print("GEOSException")

def export_wing(surf, index):
  filename = f"output/wing_{str(index).zfill(3)}.png"
  result = pygame.Surface(screen.get_size())
  result.fill((0, 0, 0))
  result.blit(surf)

  pygame.image.save(result, f"{filename}")
  print(f"Saved wing {filename}")

def save_screenshot(surf, index):
  filename = f"output/orthoptera_{str(index).zfill(3)}.png"
  pygame.image.save(surf, f"{filename}")
  print(f"Saved screenshot {filename}")

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
wing_surf = pygame.Surface(screen.get_size())
wing_surf = wing_surf.convert_alpha(screen)

pygame.display.set_caption("Orthoptera")
clock = pygame.time.Clock()
running = True
dt = 0

uimanager = pygame_gui.UIManager((SCREEN_WIDTH, SCREEN_HEIGHT), theme_path="theme.json")
slider_panel = SliderPanel(
  parameters=parameters,
  relative_rect=pygame.Rect((SCREEN_WIDTH - 10 - SLIDER_PANEL_WIDTH, 25), (SLIDER_PANEL_WIDTH, SCREEN_HEIGHT - 50)),
  manager=uimanager)

slider_param_names = [
  # "alpha",

  # "max_generations_const",
  # "max_generations_linear",
  # "max_generations_quadratic",

  # "root_segment_len",
  # "segment_len_factor",

  # "root_segment_pos_const_x",
  # "root_segment_pos_const_y",
  "root_segment_pos_linear_x",
  "root_segment_pos_linear_y",
  "root_segment_pos_quadratic_x",
  "root_segment_pos_quadratic_y",

  "root_segment_dir_const_x",
  "root_segment_dir_const_y",
  "root_segment_dir_linear_x",
  "root_segment_dir_linear_y",
  "root_segment_dir_quadratic_x",
  "root_segment_dir_quadratic_y",

  "segment_dir_linear_x",
  "segment_dir_linear_y",
  "segment_dir_quadratic_x",
  "segment_dir_quadratic_y",

  # "segment_dir_a_x",
  # "segment_dir_a_y",
  # "segment_dir_b_x",
  # "segment_dir_b_y",
  # "segment_dir_c_x",
  # "segment_dir_c_y",
  # "segment_dir_d_x",
  # "segment_dir_d_y",
]
for name in slider_param_names:
  slider_panel.add_slider(param_defs[name])

fps_array = []

parameters_changed()

while running:
  for event in pygame.event.get():
    if event.type == pygame.QUIT:
      running = False
    elif event.type == pygame.KEYDOWN:
      if event.key == pygame.K_ESCAPE:
        running = False
      elif event.key == pygame.K_l:
        load_parameters()
        parameters_changed()
      elif event.key == pygame.K_1:
        randomize_base_parameters()
      elif event.key == pygame.K_2:
        randomize_primary_vein_parameters()
        parameters_changed()
      elif event.key == pygame.K_3:
        vein_renderer.generate_cross_veins()
      elif event.key == pygame.K_r:
        save_screenshot(screen, screenshot_index)
        screenshot_index += 1
      elif event.key == pygame.K_v:
        save_parameters()
      elif event.key == pygame.K_x:
        export_wing(wing_surf, export_index)
        export_index += 1
      elif event.key == pygame.K_m:
        if mode == EDIT_MODE:
          mode = PREVIEW_MODE
        elif mode == PREVIEW_MODE:
          mode = EDIT_MODE

    slider_panel.process_events(event, parameters_changed)
    uimanager.process_events(event)

  uimanager.update(dt)

  screen.fill("black")

  wing_surf.fill((0, 0, 0, 0))
  vein_renderer.render_to(wing_surf, RENDER_OFFSET)
  screen.blit(wing_surf)

  render_hud(screen, floor(np.average(fps_array)) if len(fps_array) else 0)

  if mode == EDIT_MODE:
    uimanager.draw_ui(screen)

  pygame.display.flip()

  dt = clock.tick(MAX_FPS) / 1000

  fps_array.append(1 / dt)
  fps_array = fps_array[:10]

pygame.quit()