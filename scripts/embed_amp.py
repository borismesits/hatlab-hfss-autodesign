from pyaedt import Hfss
import numpy as np
import pyEPR as epr
import pandas as pd
import tube_physics
from designer import TubeDesigner

if __name__ == '__main__':

    designer = TubeDesigner(r'D:\Ansoft', r'Embedded Amp 2025', r'EA_cooldown20250218_B2',updateDesignOn=False)


    designer.add_resonator('res1', 'res1')
    designer.add_resonator('res2', 'res2')
    designer.add_resonator('res4', 'res4')

    designer.add_transmon('qb1', 'qb1', 'Lj_1', 'junc_qb1', 'line_qb1')
    designer.add_transmon('qb2', 'qb2', 'Lj_2', 'junc_qb2', 'line_qb2')
    designer.add_SNAIL('SNAIL', 'snail', 'Lj_snail', 'junc_snail', 'line_snail', snail_alpha=0.25, snail_n=2, snail_m=1)

    designer.add_target(target_type='resonator_freq', target_val=5.8e9, design_var='res_1_l', mode1='res1', tol=10e6)
    designer.add_target(target_type='resonator_freq', target_val=6.5e9, design_var='res_2_l', mode1='res2', tol=10e6)
    designer.add_target(target_type='resonator_freq', target_val=7.5e9, design_var='res_4_l', mode1='res4', tol=10e6)

    designer.add_target(target_type='transmon_freq', target_val=4.3e9, design_var='Lj_1', mode1='qb1', tol=10e6)
    designer.add_target(target_type='alpha', target_val=200e6, design_var='pad_qb1_l', mode1='qb1', tol=10e6)
    designer.add_target(target_type='transmon_freq', target_val=4.4e9, design_var='Lj_2', mode1='qb2', tol=10e6)
    designer.add_target(target_type='alpha', target_val=200e6, design_var='pad_qb2_l', mode1='qb2', tol=10e6)

    designer.add_target(target_type='SNAIL_freq', target_val=4.0e9, design_var='pad_snail_l', mode1='SNAIL', tol=10e6)

    designer.add_target(target_type='chi', target_val=5e6, design_var='readgap_1', mode1='qb1', mode2='res1', tol=1e6, speed=0.5)
    designer.add_target(target_type='chi', target_val=5e6, design_var='readgap_2', mode1='qb2', mode2='res2', tol=1e6, speed=0.5)

    designer.add_target(target_type='snail_g3', target_val=30e6, design_var='Lj_snail', mode1='SNAIL', tol=5e6,
                        speed=0.1)
    designer.add_target(target_type='g2eff', target_val=1.5e6, design_var='swapgap_1', mode1='SNAIL', mode2='res1',
                        tol=0.5e6, speed=0.1)
    designer.add_target(target_type='g2eff', target_val=1.5e6, design_var='swapgap_2', mode1='SNAIL', mode2='res2',
                        tol=0.5e6, speed=0.2)
    designer.add_target(target_type='g2eff', target_val=1.5e6, design_var='swapgap_4', mode1='SNAIL', mode2='res4',
                        tol=0.5e6, speed=0.2)

    designer.add_target(target_type='kappa', target_val=0.1e6, design_var='res1_pin_z', mode1='res1',
                        tol=0.02e6, speed=0.4)
    designer.add_target(target_type='kappa', target_val=0.1e6, design_var='res2_pin_z', mode1='res2',
                        tol=0.02e6, speed=0.4)
    designer.add_target(target_type='kappa', target_val=50e6, design_var='res4_pin_z', mode1='res4',
                        tol=5e6, speed=0.4)

    designer.init_EPR()
    designer.iterate_loop(max_num=1)




