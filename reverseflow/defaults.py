"""Default mappings between parametric inverses and inverses"""
from arrows.primitive.math_arrows import *
from arrows.primitive.control_flow import *
from reverseflow.dispatch import *

default_dispatch = {AddArrow: inv_add,
                    SubArrow: inv_sub,
                    CosArrow: inv_cos,
                    DuplArrow: inv_dupl_approx,
                    ExpArrow: inv_exp,
                    GatherArrow: inv_gather,
                    MulArrow: inv_mul,
                    NegArrow: inv_neg,
                    ReshapeArrow: inv_reshape,
                    SinArrow: inv_sin,
                    }

# default_dispatch = {AddArrow: inv_add,
#                     SubArrow: inv_sub,
#                     MulArrow: inv_mul,
#                     DivArrow: inv_div,
#                     DuplArrow: inv_dupl_approx}
