from typing import TypedDict

class Parameters(TypedDict):
  num_root_segments: int
  root_segment_pos: tuple[float, float]
  root_segment_pos_offset: tuple[float, float]
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
      root_segment_pos=(295, 340),
      root_segment_pos_offset=(-5, 10),
      root_segment_len=100,
      root_segment_len_factor=0.9,
      root_segment_dir=(1, -0.2),
      root_segment_dir_offset=4,
      segment_len_factor=0.95,
      segment_dir_offset=2,
      max_generations=12
    )

  def group(prefix):
    pass