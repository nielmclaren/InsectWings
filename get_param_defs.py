from typing import Dict

from param_def import ParamDef

def get_param_defs() -> Dict[str, ParamDef]:
  return {d.name: d for d in [
    ParamDef("alpha", "int", (0, 255)),
    ParamDef("num_root_segments", "int", (12, 12)),
    ParamDef("root_segment_pos_const_x", "int", (0, 1920)),
    ParamDef("root_segment_pos_const_y", "int", (0, 1080)),
    ParamDef("root_segment_pos_linear_x", "float", (-30, 30)),
    ParamDef("root_segment_pos_linear_y", "float", (-30, 30)),
    ParamDef("root_segment_pos_quadratic_x", "float", (-5, 5)),
    ParamDef("root_segment_pos_quadratic_y", "float", (-5, 5)),
    ParamDef("root_segment_len", "float", (0, 100)),
    ParamDef("root_segment_dir_const_x", "float", (0, 10)),
    ParamDef("root_segment_dir_const_y", "float", (-10, 10)),
    ParamDef("root_segment_dir_linear_x", "float", (-5, 5)),
    ParamDef("root_segment_dir_linear_y", "float", (-5, 5)),
    ParamDef("root_segment_dir_quadratic_x", "float", (-0.5, 0.5)),
    ParamDef("root_segment_dir_quadratic_y", "float", (-0.5, 0.5)),
    ParamDef("segment_dir_linear_x", "float", (-1, 1)),
    ParamDef("segment_dir_linear_y", "float", (-1, 1)),
    ParamDef("segment_dir_quadratic_x", "float", (-0.1, 0.1)),
    ParamDef("segment_dir_quadratic_y", "float", (-0.1, 0.1)),
    ParamDef("segment_dir_a_x", "float", (-0.01, 0.01)),
    ParamDef("segment_dir_a_y", "float", (-0.01, 0.01)),
    ParamDef("segment_dir_b_x", "float", (-0.05, 0.05)),
    ParamDef("segment_dir_b_y", "float", (-0.05, 0.05)),
    ParamDef("segment_dir_c_x", "float", (-0.05, 0.05)),
    ParamDef("segment_dir_c_y", "float", (-0.05, 0.05)),
    ParamDef("segment_dir_d_x", "float", (-0.1, 0.1)),
    ParamDef("segment_dir_d_y", "float", (-0.1, 0.1)),
    ParamDef("segment_len_factor", "float", (0.2, 1.2)),
    ParamDef("max_generations_const", "int", (0, 100)),
    ParamDef("max_generations_linear", "float", (-10, 10)),
    ParamDef("max_generations_quadratic", "float", (-1, 1))
  ]}