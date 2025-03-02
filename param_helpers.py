import pygame

def param_to_vector2(parameters, prefix):
    return pygame.Vector2(parameters[f"{prefix}_x"], parameters[f"{prefix}_y"])

def quadratic_param_to_vector2(parameters, x):
    return param_to_vector2(parameters, 'quadratic') * pow(x, 2) + \
        param_to_vector2(parameters, 'linear') * x + \
        param_to_vector2(parameters, 'const')
