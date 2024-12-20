from typing import TypedDict

class ParamSet(TypedDict):
  alpha: int
  reference_alpha: int
  num_root_segments: int
  root_segment_pos_const_x: float
  root_segment_pos_const_y: float
  root_segment_pos_linear_x: float
  root_segment_pos_linear_y: float
  root_segment_pos_quadratic_x: float
  root_segment_pos_quadratic_y: float
  root_segment_len: float
  root_segment_len_factor: float
  root_segment_dir_const_x: float
  root_segment_dir_const_y: float
  root_segment_dir_linear_x: float
  root_segment_dir_linear_y: float
  root_segment_dir_quadratic_x: float
  root_segment_dir_quadratic_y: float
  segment_dir_linear_x: float
  segment_dir_linear_y: float
  segment_dir_quadratic_x: float
  segment_dir_quadratic_y: float
  segment_dir_a_x: float
  segment_dir_a_y: float
  segment_dir_b_x: float
  segment_dir_b_y: float
  segment_dir_c_x: float
  segment_dir_c_y: float
  segment_dir_d_x: float
  segment_dir_d_y: float
  segment_len_factor: float
  max_generations_const: int
  max_generations_linear: float
  max_generations_quadratic: float

  def defaults():
    return ParamSet(
      alpha=96,
      reference_alpha=192,
      num_root_segments=12,
      root_segment_pos_const_x=295,
      root_segment_pos_const_y=340,
      root_segment_pos_linear_x=-5,
      root_segment_pos_linear_y=10,
      root_segment_pos_quadratic_x=0,
      root_segment_pos_quadratic_y=0,
      root_segment_len=100,
      root_segment_len_factor=0.9,
      root_segment_dir_const_x=1,
      root_segment_dir_const_y=-0.2,
      root_segment_dir_linear_x=0,
      root_segment_dir_linear_y=0,
      root_segment_dir_quadratic_x=0,
      root_segment_dir_quadratic_y=0,
      segment_dir_linear_x=0,
      segment_dir_linear_y=0,
      segment_dir_quadratic_x=0,
      segment_dir_quadratic_y=0,
      segment_dir_a_x=0,
      segment_dir_a_y=0,
      segment_dir_b_x=0,
      segment_dir_b_y=0,
      segment_dir_c_x=0,
      segment_dir_c_y=0,
      segment_dir_d_x=0,
      segment_dir_d_y=0,
      segment_len_factor=0.95,
      max_generations_const=12,
      max_generations_linear=0.0,
      max_generations_quadratic=0.0
    )