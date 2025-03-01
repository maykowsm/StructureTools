from .distri_load_cmd import DistLoadCmd
from .pontual_momentum_cmd  import PontualMomentumLoadCmd
from .pontual_force_cmd import PontualForceLoadCmd

group_name = "Structure Load Tools"
cmd_list = [DistLoadCmd, PontualForceLoadCmd, PontualMomentumLoadCmd]