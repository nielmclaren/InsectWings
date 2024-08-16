#!/usr/bin/python3

from math import floor
import numpy as np
import pygame

# Reaction-Diffusion algorithm adapted from Reddit user Doormatty.
# https://www.reddit.com/r/Python/comments/og8vh6/comment/h4k2408/?utm_source=share&utm_medium=web3x&utm_name=web3xcss&utm_term=1&utm_content=share_button

width = 320
height = 320

pygame.init()
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("Reaction-Diffusion")
clock = pygame.time.Clock()
running = True
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
  f = 0.018 # Feed rate
  k = 0.051 # Kill rate
  dt = 1 # Time step

  alpha = grid[:, :, 0]
  beta = grid[:, :, 1]
  newalpha = constrain(alpha + (1.0 * laplace2d(alpha) - alpha * beta * beta + f * (1 - alpha)) * dt, 0, 1)
  newbeta = constrain(beta + (0.5 * laplace2d(beta) + alpha * beta * beta - (k + f) * beta) * dt, 0, 1)
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
  pygame.display.flip()

  dt = clock.tick(60) / 1000 # Set 60 FPS limit
  fps_array.append(1 / dt)
  fps_array = fps_array[:20]
  print(floor(np.average(fps_array)))

pygame.quit()
