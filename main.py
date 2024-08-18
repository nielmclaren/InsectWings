#!/usr/bin/python3

from math import floor
import numpy as np
import pygame
import pygame.freetype

# Reaction-Diffusion algorithm adapted from Reddit user Doormatty.
# https://www.reddit.com/r/Python/comments/og8vh6/comment/h4k2408/?utm_source=share&utm_medium=web3x&utm_name=web3xcss&utm_term=1&utm_content=share_button

grid_width = 320
grid_height = 32

TIME_STEP = 1

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

def get_cases(feed_rate, feed_rate_window_size, kill_rate, kill_rate_window_size, num_cases_per):
  feed_rate_low = feed_rate - feed_rate_window_size/2
  kill_rate_low = kill_rate - kill_rate_window_size/2
  feed_rate_step = feed_rate_window_size / num_cases_per
  kill_rate_step = kill_rate_window_size / num_cases_per
  return [(round(feed_rate_low + (x % num_cases_per) * feed_rate_step, 3),
           round(kill_rate_low + floor(x / num_cases_per) * kill_rate_step, 3)) for x in range(0, num_cases_per * num_cases_per)]

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

def update(grid):
  alpha = grid[:, :, 0]
  beta = grid[:, :, 1]
  newalpha = constrain(alpha + (diffuse_a * laplace2d(alpha) - alpha * beta * beta + feed_rate * (1 - alpha)) * TIME_STEP, 0, 1)
  newbeta = constrain(beta + (diffuse_b * laplace2d(beta) + alpha * beta * beta - (kill_rate + feed_rate) * beta) * TIME_STEP, 0, 1)
  retval = np.dstack([newalpha, newbeta])
  return retval

def get_color(grid):
  c_arr = np.zeros((grid_width, grid_height, 3), dtype=np.uint8)
  c = np.floor((grid[:, :, 0] - grid[:, :, 1]) * 255)
  c_arr[:, :, 0] = constrain(255 - c, 0, 255)
  c_arr[:, :, 1] = constrain(55 - c, 0, 255)
  c_arr[:, :, 2] = constrain(155 - c, 0, 255)
  return c_arr


cases = get_cases(0.025, 0.003, 0.050, 0.003, 6)
total_cases = len(cases)
for case_index in range(0, total_cases):
  (feed_rate, kill_rate) = cases[case_index]
  print(f"({case_index+1} / {total_cases}) Feed rate: {feed_rate}, Kill rate: {kill_rate}")
print()
case_index = 0
(feed_rate, kill_rate) = cases[case_index]
print(f"({case_index+1}) Feed rate: {feed_rate}, Kill rate: {kill_rate}")
main_grid = init_grid()

while running:
  for event in pygame.event.get():
    if event.type == pygame.QUIT:
      running = False
    elif event.type == pygame.KEYDOWN:
      if event.key == pygame.K_ESCAPE:
        running = False

  for i in range(8):
    main_grid = update(main_grid)
    step += 1

  canvas = get_color(main_grid)
  display_surf = pygame.surfarray.make_surface(canvas)

  screen.fill("black")
  screen.blit(display_surf, (0, 128))

  hud_pos = [10, 10]
  HUD_FONT.render_to(screen, hud_pos, f"Diffuse A: {diffuse_a}", (255, 255, 255))
  hud_pos[1] += 18
  HUD_FONT.render_to(screen, hud_pos, f"Diffuse B: {diffuse_b}", (255, 255, 255))
  hud_pos[1] += 18
  HUD_FONT.render_to(screen, hud_pos, f"Feed: {feed_rate}", (255, 255, 255))
  hud_pos[1] += 18
  HUD_FONT.render_to(screen, hud_pos, f"Kill: {kill_rate}", (255, 255, 255))
  hud_pos[1] += 18
  HUD_FONT.render_to(screen, hud_pos, f"Step: {step}", (255, 255, 255))

  pygame.display.flip()

  dt = clock.tick(60) / 1000 # Set 60 FPS limit
  fps_array.append(1 / dt)
  fps_array = fps_array[:20]
  #print(floor(np.average(fps_array)))

  if step >= 1600:
    f = f"{feed_rate}"[2:5]
    k = f"{kill_rate}"[2:5]
    filename = f"output_s{step}_f{f}_k{k}.png"
    pygame.image.save(screen, f"output/{filename}")
    print(f"Saved {filename}")

    case_index += 1
    if case_index >= len(cases):
      print("Finished all cases.")
      break
    (feed_rate, kill_rate) = cases[case_index]
    print(f"({case_index+1} / {total_cases}) Feed rate: {feed_rate}, Kill rate: {kill_rate}")
    main_grid = init_grid()
    step = 0

pygame.quit()
