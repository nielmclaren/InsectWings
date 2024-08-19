#!/usr/bin/python3

import dataclasses
from dataclasses import dataclass
from math import floor
import numpy as np
import pygame
import pygame.freetype

# Reaction-Diffusion algorithm adapted from Reddit user Doormatty.
# https://www.reddit.com/r/Python/comments/og8vh6/comment/h4k2408/?utm_source=share&utm_medium=web3x&utm_name=web3xcss&utm_term=1&utm_content=share_button

@dataclass
class Case:
    feed_rate: float = 0.0
    kill_rate: float = 0.0
    diffuse_a: float = 0.0
    diffuse_b: float = 0.0
    time_step: float = 0.0

grid_width = 320
grid_height = 32

pygame.init()
pygame.freetype.init()
HUD_FONT = pygame.freetype.Font("DejaVuSansMono.ttf", 12)
screen = pygame.display.set_mode((320, 160))
pygame.display.set_caption("Reaction-Diffusion")
clock = pygame.time.Clock()
running = True
step = 0
dt = 0
fps_array = []

diffuse_a = 1.0
diffuse_b = 0.5
seed_size = 16

def get_cases(base_case, x_name, x_window_size, y_name, y_window_size, num_cases_each):
  x_low = base_case.__dict__[x_name] - x_window_size/2
  y_low = base_case.__dict__[y_name] - y_window_size/2
  x_step = x_window_size / num_cases_each
  y_step = y_window_size / num_cases_each
  return [dataclasses.replace(base_case, **{
    x_name: round(x_low + (index % num_cases_each) * x_step, 5),
    y_name: round(y_low + floor(index / num_cases_each) * y_step, 5),
  }) for index in range(0, num_cases_each * num_cases_each)]

def print_case(c, total_cases):
  print(f"({case_index+1} / {total_cases}) Diffuse A: {c.diffuse_a} Diffuse B: {c.diffuse_b} Feed rate: {c.feed_rate}, Kill rate: {c.kill_rate}")

def init_grid():
  # Each element is an array of two values representing the concentration of two chemicals.
  grid = np.zeros((grid_width, grid_height, 2), dtype=np.float32)
  grid[0:grid_width, 0:grid_height] = [1, 0]
  grid[0:seed_size, 0:grid_height] = [0, 1]
  return grid

def laplace2d(grid):
  laplace = np.array([[0.05, 0.2, 0.05], [0.2, -1, 0.2], [0.05, 0.2, 0.05]])
  view = np.lib.stride_tricks.sliding_window_view(grid, (3, 3))
  # TODO: Why use negative axis parameters?
  result = np.sum(view * laplace, axis=(-1, -2))
  # TODO: What does the padding do?
  result = np.pad(result, pad_width=1)
  return result

def constrain(value, min_limit, max_limit):
  return np.minimum(max_limit, np.maximum(min_limit, value))

def update(case, grid):
  alpha = grid[:, :, 0]
  beta = grid[:, :, 1]
  newalpha = constrain(alpha + (case.diffuse_a * laplace2d(alpha) - alpha * beta * beta + case.feed_rate * (1 - alpha)) * case.time_step, 0, 1)
  newbeta = constrain(beta + (case.diffuse_b * laplace2d(beta) + alpha * beta * beta - (case.kill_rate + case.feed_rate) * beta) * case.time_step, 0, 1)
  retval = np.dstack([newalpha, newbeta])
  return retval

def get_color(grid):
  c_arr = np.zeros((grid_width, grid_height, 3), dtype=np.uint8)
  c = np.floor((grid[:, :, 0] - grid[:, :, 1]) * 255)
  c_arr[:, :, 0] = constrain(255 - c, 0, 255)
  c_arr[:, :, 1] = constrain(55 - c, 0, 255)
  c_arr[:, :, 2] = constrain(155 - c, 0, 255)
  return c_arr

def render_hud_to(surf, case_index, total_cases, case, step):
  text_color = (255, 255, 255)
  hud_pos = [10, 10]
  HUD_FONT.render_to(surf, hud_pos, f"Case: {case_index+1} / {total_cases}", text_color)
  hud_pos[1] += 18
  HUD_FONT.render_to(surf, hud_pos, f"Diffuse A: {case.diffuse_a}", text_color)
  hud_pos[1] += 18
  HUD_FONT.render_to(surf, hud_pos, f"Diffuse B: {case.diffuse_b}", text_color)
  hud_pos[1] += 18
  HUD_FONT.render_to(surf, hud_pos, f"Feed: {case.feed_rate}", text_color)
  hud_pos[1] += 18
  HUD_FONT.render_to(surf, hud_pos, f"Kill: {case.kill_rate}", text_color)
  hud_pos[1] += 18
  HUD_FONT.render_to(surf, hud_pos, f"Step: {step}", text_color)

#base_case = Case(feed_rate=0.025, kill_rate=0.05, diffuse_a=1.0, diffuse_b=0.5, time_step=1.0)
#cases = get_cases(base_case, 'feed_rate', 0.003, 'kill_rate', 0.003, 6)
base_case = Case(feed_rate=0.025, kill_rate=0.05, diffuse_a=0.92, diffuse_b=0.5, time_step=1.0)
cases = get_cases(base_case, 'diffuse_a', 0.24, 'diffuse_b', 0.24, 6)
total_cases = len(cases)
for case_index in range(0, total_cases):
  print_case(cases[case_index], total_cases)
  
print()
case_index = 0
print_case(cases[case_index], total_cases)
main_grid = init_grid()

while running:
  for event in pygame.event.get():
    if event.type == pygame.QUIT:
      running = False
    elif event.type == pygame.KEYDOWN:
      if event.key == pygame.K_ESCAPE:
        running = False

  for i in range(8):
    main_grid = update(cases[case_index], main_grid)
    step += 1

  canvas = get_color(main_grid)
  display_surf = pygame.surfarray.make_surface(canvas)

  screen.fill("black")
  screen.blit(display_surf, (0, 128))

  render_hud_to(screen, case_index, total_cases, cases[case_index], step)

  pygame.display.flip()

  dt = clock.tick(60) / 1000 # Set 60 FPS limit
  fps_array.append(1 / dt)
  fps_array = fps_array[:20]
  #print(floor(np.average(fps_array)))

  if step >= 1600:
    filename = f"output_{str(case_index).zfill(3)}.png"
    pygame.image.save(screen, f"output/{filename}")
    print(f"Saved {filename}")

    case_index += 1
    if case_index >= len(cases):
      print("Finished all cases.")
      break
    print_case(cases[case_index], total_cases)
    main_grid = init_grid()
    step = 0

pygame.quit()
