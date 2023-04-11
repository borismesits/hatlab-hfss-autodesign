from pyaedt import Hfss
import numpy as np
import pyEPR as epr
import pandas as pd
import tube_physics
from designer import TubeDesigner


if __name__ == '__main__':

    designer = TubeDesigner(r'C:/Users/hatlab-boris/Documents/Ansoft/', r'Embed_Amp', r'embed_amp_auto_20230411')

    designer.add_resonator('res1', 'res1')
    designer.add_resonator('res2', 'res2')
    designer.add_resonator('res3', 'res3')
    designer.add_resonator('res4', 'res4')
    designer.add_transmon('qb1', 'qb1', 'LJ1', 'junc1', 'J_line1')
    designer.add_transmon('qb2', 'qb2', 'LJ2', 'junc2', 'J_line2')
    designer.add_transmon('qb3', 'qb3', 'LJ3', 'junc3', 'J_line3')
    designer.add_SNAIL('SNAIL', 'snail', 'LJsnail', 'junc_snail', 'J_line_snail', snail_alpha=0.25, snail_n=3, snail_m=1)

    #
    # designer.add_target(target_type='resonator_freq', target_val=5.9e9, design_var='res1_l', mode1='res1', tol=10e6)
    # designer.add_target(target_type='resonator_freq', target_val=6.4e9, design_var='res2_l', mode1='res2', tol=10e6)
    # designer.add_target(target_type='resonator_freq', target_val=7.0e9, design_var='res3_l', mode1='res3', tol=10e6)
    # designer.add_target(target_type='resonator_freq', target_val=7.5e9, design_var='res4_l', mode1='res4', tol=10e6)
    #
    # designer.add_target(target_type='transmon_freq', target_val=5e9, design_var='LJ1', mode1='qb1', tol=10e6)
    # designer.add_target(target_type='alpha', target_val=200e6, design_var='qb1_pad', mode1='qb1', tol=10e6)
    # designer.add_target(target_type='transmon_freq', target_val=5e9, design_var='LJ2', mode1='qb2', tol=10e6)
    # designer.add_target(target_type='alpha', target_val=200e6, design_var='qb2_pad', mode1='qb2', tol=10e6)
    # designer.add_target(target_type='transmon_freq', target_val=5e9, design_var='LJ3', mode1='qb3', tol=10e6)
    # designer.add_target(target_type='alpha', target_val=200e6, design_var='qb3_pad', mode1='qb3', tol=10e6)
    #
    # designer.add_target(target_type='SNAIL_freq', target_val=200e6, design_var='LJsnail', mode1='SNAIL', tol=10e6)
    #
    # designer.add_target(target_type='chi', target_val=5e6, design_var='gap_1', mode1='qb1', mode2='res1', tol=1e6, speed=0.5)
    # designer.add_target(target_type='chi', target_val=5e6, design_var='gap_2', mode1='qb2', mode2='res2', tol=1e6, speed=0.5)
    # designer.add_target(target_type='chi', target_val=5e6, design_var='gap_3', mode1='qb3', mode2='res3', tol=1e6, speed=0.5)

    designer.add_target(target_type='snail_g3', target_val=75e6, design_var='snail_pad', mode1='SNAIL', tol=25e6,
                        speed=0.2)
    designer.add_target(target_type='g2eff', target_val=7.5e6, design_var='snail_gap_1', mode1='SNAIL', mode2='res1',
                        tol=2.5e6, speed=0.2)
    # designer.add_target(target_type='g2_eff', target_val=10e6, design_var='snaiL_gap_2', mode1='SNAIL', mode2='res2',
    #                     tol=5e6, speed=0.2)
    # designer.add_target(target_type='g2_eff', target_val=10e6, design_var='snaiL_gap_3', mode1='SNAIL', mode2='res3',
    #                     tol=5e6, speed=0.2)
    # designer.add_target(target_type='g2_eff', target_val=10e6, design_var='snaiL_gap_4', mode1='SNAIL', mode2='res4',
    #                     tol=5e6, speed=0.2)
    #
    # designer.add_WISPE_target(design_var='wispeX', mode1='qb1', cutoff=4e8, units='mm', guess_step=0.5)
    # designer.add_WISPE_target(design_var='wispeX', mode1='qb2', cutoff=4e8, units='mm', guess_step=0.5)
    # designer.add_WISPE_target(design_var='wispeX', mode1='qb3', cutoff=4e8, units='mm', guess_step=0.5)

    designer.init_EPR()
    designer.iterate_loop()




