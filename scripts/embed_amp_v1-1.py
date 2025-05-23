from pyaedt import Hfss
import numpy as np
import pyEPR as epr
import pandas as pd
import tube_physics
from designer import TubeDesigner

'''
Chasing optimal fidelity. large couplings, more parastic measurements, potentially faster purcell decay. 

Also changing the optimization. Now no longer directly targeting g3 and g2eff (problematic because you don't know
participation ratio without running an Lj sweep). Also tricky to solve for zero-flux Ej when you supply kerr-null
Ej, although the SNAIL code seems to have calculated this (details are not quite clear).

In any case, we just optimize g/Delta among modes. Then after these optimization sims are done, we run a final Lj sweep,
check Qs when we turn ports on/off, and use SNAIL notebook to calculate the zero-flux Lj to target, and the actual
rates g3 and g2eff we get. This makes sense because we are not really optimizing these: we will just take the biggest number
possible for g3.
'''

if __name__ == '__main__':

    designer = TubeDesigner(r'D:\Ansoft', r'Embedded Amp 2025', r'EA_cooldown20250218_B2',updateDesignOn=False)

    designer.add_resonator('res1', 'res1')
    designer.add_resonator('res2', 'res2')
    designer.add_resonator('res3', 'res3')
    designer.add_resonator('res4', 'res4')

    designer.add_transmon('qb1', 'qb1', 'Lj_1', 'junc_qb1', 'line_qb1')
    designer.add_transmon('qb2', 'qb2', 'Lj_2', 'junc_qb2', 'line_qb2')
    designer.add_transmon('qb3', 'qb3', 'Lj_3', 'junc_qb3', 'line_qb3')
    designer.add_SNAIL('SNAIL', 'snail', 'Lj_snail', 'junc_snail', 'line_snail', snail_alpha=0.25, snail_n=2, snail_m=1)

    designer.add_target(target_type='resonator_freq', target_val=5.8e9, design_var='res_1_l', mode1='res1', tol=10e6)
    designer.add_target(target_type='resonator_freq', target_val=6.5e9, design_var='res_2_l', mode1='res2', tol=10e6)
    designer.add_target(target_type='resonator_freq', target_val=7.2e9, design_var='res_3_l', mode1='res3', tol=10e6)
    designer.add_target(target_type='resonator_freq', target_val=7.5e9, design_var='res_4_l', mode1='res4', tol=10e6)

    designer.add_target(target_type='transmon_freq', target_val=2.0e9, design_var='Lj_1', mode1='qb1', tol=10e6)
    designer.add_target(target_type='alpha', target_val=100e6, design_var='pad_qb1_l', mode1='qb1', tol=10e6)
    designer.add_target(target_type='transmon_freq', target_val=2.2e9, design_var='Lj_2', mode1='qb2', tol=10e6)
    designer.add_target(target_type='alpha', target_val=100e6, design_var='pad_qb2_l', mode1='qb2', tol=10e6)
    designer.add_target(target_type='transmon_freq', target_val=2.4e9, design_var='Lj_3', mode1='qb3', tol=10e6)
    designer.add_target(target_type='alpha', target_val=100e6, design_var='pad_qb3_l', mode1='qb3', tol=10e6)

    designer.add_target(target_type='SNAIL_freq', target_val=4.0e9, design_var='pad_snail_l', mode1='SNAIL', tol=10e6)

    designer.add_target(target_type='chi', target_val=2e6, design_var='readgap_1', mode1='qb1', mode2='res1', tol=1e6,
                        speed=0.5)
    designer.add_target(target_type='chi', target_val=2e6, design_var='readgap_2', mode1='qb2', mode2='res2', tol=1e6,
                        speed=0.5)
    designer.add_target(target_type='chi', target_val=2e6, design_var='readgap_3', mode1='qb3', mode2='res3', tol=1e6,
                        speed=0.5)

    # designer.add_target(target_type='snail_g3', target_val=30e6, design_var='Lj_snail', mode1='SNAIL', tol=5e6,
    #                     speed=0.1)
    # designer.add_target(target_type='g2eff', target_val=1.5e6, design_var='swapgap_1', mode1='SNAIL', mode2='res1',
    #                     tol=0.5e6, speed=0.1)
    # designer.add_target(target_type='g2eff', target_val=1.5e6, design_var='swapgap_2', mode1='SNAIL', mode2='res2',
    #                     tol=0.5e6, speed=0.2)
    # designer.add_target(target_type='g2eff', target_val=1.5e6, design_var='swapgap_4', mode1='SNAIL', mode2='res4',
    #                     tol=0.5e6, speed=0.2)
    # designer.add_target(target_type='g2eff', target_val=1.5e6, design_var='swapgap_4', mode1='SNAIL', mode2='res4',
    #                     tol=0.5e6, speed=0.2)

    designer.add_target(target_type='g_delta', target_val=0.1, design_var='swapgap_4', mode1='SNAIL', mode2='res4',
                        tol=0.01, speed=0.2)
    designer.add_target(target_type='g_delta', target_val=0.1, design_var='swapgap_4', mode1='SNAIL', mode2='res4',
                        tol=0.01, speed=0.2)
    designer.add_target(target_type='g_delta', target_val=0.1, design_var='swapgap_4', mode1='SNAIL', mode2='res4',
                        tol=0.01, speed=0.2)
    designer.add_target(target_type='g_delta', target_val=0.1, design_var='swapgap_4', mode1='SNAIL', mode2='res4',
                        tol=0.01, speed=0.2)

    designer.add_target(target_type='kappa', target_val=0.1e6, design_var='res1_pin_z', mode1='res1',
                        tol=0.02e6, speed=0.4)
    designer.add_target(target_type='kappa', target_val=0.1e6, design_var='res2_pin_z', mode1='res2',
                        tol=0.02e6, speed=0.4)
    designer.add_target(target_type='kappa', target_val=50e6, design_var='res4_pin_z', mode1='res4',
                        tol=5e6, speed=0.4)

    designer.init_EPR()
    designer.iterate_loop(max_num=1)


    '''
    todo: add another class, like evalulator or processor, that runs after optimization is complete. It will run an
    Lj sweep on the snail to get L, C, and thus participation and all the amp parameters, and the desired resistance 
    at RT. At desired KN, it will also turn losses on and off to get a full kappa matrix.
    
    It will generate a report on everything. Maybe will interface with frequency crowding code. Parastic measurements.
    All parametric rates. Dephasing times from thermal photons at all ports. Drive parameters 
    '''


