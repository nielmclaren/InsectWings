from typing import TypedDict

class Parameters(TypedDict):
  num_root_segments: int
  root_segment_pos_const_x: float
  root_segment_pos_const_y: float
  root_segment_pos_linear_x: float
  root_segment_pos_linear_y: float
  root_segment_pos_quadratic_x: float
  root_segment_pos_quadratic_y: float
  root_segment_len: float
  root_segment_len_factor: float
  root_segment_dir: tuple[float, float]
  root_segment_dir_offset: float
  segment_len_factor: float
  segment_dir_offset: float
  max_generations: int

  def defaults():
    return Parameters(
      num_root_segments=12,
      root_segment_pos_const_x=295,
      root_segment_pos_const_y=340,
      root_segment_pos_linear_x=-5,
      root_segment_pos_linear_y=10,
      root_segment_pos_quadratic_x=0,
      root_segment_pos_quadratic_y=0,
      root_segment_len=100,
      root_segment_len_factor=0.9,
      root_segment_dir=(1, -0.2),
      root_segment_dir_offset=4,
      segment_len_factor=0.95,
      segment_dir_offset=2,
      max_generations=12
    )