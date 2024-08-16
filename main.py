#!/usr/bin/python3

from math import floor
import numpy as np
import pygame
import pygame.freetype

# Reaction-Diffusion algorithm adapted from Reddit user Doormatty.
# https://www.reddit.com/r/Python/comments/og8vh6/comment/h4k2408/?utm_source=share&utm_medium=web3x&utm_name=web3xcss&utm_term=1&utm_content=share_button

width = 320
height = 320

FEED_RATE = 0.018
KILL_RATE = 0.051
TIME_STEP = 1


pygame.init()
pygame.freetype.init()
HUD_FONT = pygame.freetype.Font("DejaVuSansMono.ttf", 12)
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("Reaction-Diffusion")
clock = pygame.time.Clock()
running = True
step = 0
dt = 0
fps_array = []

seed_size = 20

# Each element is an array of two values representing the concentration of two chemicals.
main_grid = np.zeros((width, height, 2), dtype=np.float32)
main_grid[0:width, 0:height] = [1, 0]

w1 = floor(width / 2 - seed_size / 2)
w2 = floor(width / 2 + seed_size / 2)
h1 = floor(height / 2 - seed_size / 2)
h2 = floor(height / 2 + seed_size / 2)
main_grid[w1:w2, h1:h2] = [0, 1]

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
  newalpha = constrain(alpha + (1.0 * laplace2d(alpha) - alpha * beta * beta + FEED_RATE * (1 - alpha)) * TIME_STEP, 0, 1)
  newbeta = constrain(beta + (0.5 * laplace2d(beta) + alpha * beta * beta - (KILL_RATE + FEED_RATE) * beta) * TIME_STEP, 0, 1)
  retval = np.dstack([newalpha, newbeta])
  return retval

def get_color(grid):
  c_arr = np.zeros((width, height, 3), dtype=np.uint8)
  c = np.floor((grid[:, :, 0] - grid[:, :, 1]) * 255)
  c_arr[:, :, 0] = constrain(255 - c, 0, 255)
  c_arr[:, :, 1] = constrain(55 - c, 0, 255)
  c_arr[:, :, 2] = constrain(155 - c, 0, 255)
  return c_arr

while running:
  for event in pygame.event.get():
    if event.type == pygame.QUIT:
      running = False
    elif event.type == pygame.KEYDOWN:
      if event.key == pygame.K_ESCAPE:
        running = False

  for i in range(2):
    main_grid = update(main_grid)

  canvas = get_color(main_grid)
  display_surf = pygame.surfarray.make_surface(canvas)
  screen.blit(display_surf, (0, 0))

  hud_pos = [10, 10]
  HUD_FONT.render_to(screen, hud_pos, f"Feed: {FEED_RATE}", (255, 255, 255))
  hud_pos[1] += 18
  HUD_FONT.render_to(screen, hud_pos, f"Kill: {KILL_RATE}", (255, 255, 255))
  hud_pos[1] += 18
  HUD_FONT.render_to(screen, hud_pos, f"Step: {step}", (255, 255, 255))

  pygame.display.flip()

  dt = clock.tick(60) / 1000 # Set 60 FPS limit
  fps_array.append(1 / dt)
  fps_array = fps_array[:20]
  #print(floor(np.average(fps_array)))

  if step == 800:
    f = f"{FEED_RATE}"[2:]
    k = f"{KILL_RATE}"[2:]
    pygame.image.save(screen, f"output_f{f}_k{k}.png")
  step += 1

pygame.quit()
