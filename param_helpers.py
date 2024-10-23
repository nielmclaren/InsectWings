import pygame

def param_to_vector2(parameters, prefix):
  return pygame.Vector2(parameters[f"{prefix}_x"], parameters[f"{prefix}_y"])
