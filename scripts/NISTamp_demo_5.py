from pyaedt import Hfss
import numpy as np
import pyEPR as epr
import pandas as pd
import tube_physics
from designer import TubeDesigner

if __name__ == '__main__':

    chip_num = 2

    if chip_num == 1:

        designer = TubeDesigner(r'D:\Ansoft', r'mega_demo_5', r'tube1')
        #
        # designer.add_resonator('Resonator1', 'res1')
        #
        # designer.add_transmon('Transmon1', 'transmon_1', 'LJ_1', 'junc1', 'Polyline1')
        #
        # designer.add_target(target_type='resonator_freq', target_val=5.65e9, design_var='res_1_l', mode1='Resonator1',
        #                     tol=30e6)
        # designer.add_target(target_type='transmon_freq', target_val=3.6e9, design_var='LJ_1', mode1='Transmon1', tol=30e6)
        # designer.add_target(target_type='alpha', target_val=170e6, design_var='qb_1_pad_l', mode1='Transmon1', tol=10e6)
        # designer.add_target(target_type='chi', target_val=1e6, design_var='readgap_1', mode1='Resonator1', mode2='Transmon1',
        #                     tol=0.5e6, speed=0.4)
        #
        # # designer.add_target(target_type='kappa', target_val=2e6, design_var='res_port_z', mode1='Resonator',
        # #                     tol=0.4e6, speed=0.4)
        #
        # designer.add_WISPE_target(design_var='CS_x1', mode1='Transmon1', cutoff=4e7, units='mm', guess_step=0.5)

    if chip_num == 2:
        designer = TubeDesigner(r'D:\Ansoft', r'mega_demo_5', r'tube2', updateDesignOn=True)

        designer.add_resonator('Resonator2', 'res2')

        designer.add_transmon('Transmon2', 'transmon_2', 'LJ_2', 'junc2', 'Polyline2')

        designer.add_target(target_type='resonator_freq', target_val=5.65e9, design_var='res_2_l', mode1='Resonator2',
                            tol=3e6)
        designer.add_target(target_type='transmon_freq', target_val=3.9e9, design_var='LJ_2', mode1='Transmon2', tol=3e6)
        designer.add_target(target_type='alpha', target_val=170e6, design_var='qb_2_pad_l', mode1='Transmon2', tol=10e6)
        designer.add_target(target_type='chi', target_val=2e6, design_var='readgap_2', mode1='Resonator2',
                            mode2='Transmon2',
                            tol=0.1e6, speed=0.4)

        # designer.add_target(target_type='kappa', target_val=2e6, design_var='res_port_z', mode1='Resonator',
        #                     tol=0.4e6, speed=0.4)

        designer.add_WISPE_target(design_var='CS_x2', mode1='Transmon2', cutoff=4e7, units='mm', guess_step=0.5)

    if chip_num == 3:
        designer = TubeDesigner(r'D:\Ansoft', r'mega_demo_5', r'tube3_v2')
        designer.add_resonator('Resonator3', 'res3')

        designer.add_transmon('Transmon3', 'transmon_3', 'LJ_3', 'junc3', 'Polyline3')

        designer.add_target(target_type='resonator_freq', target_val=6.5e9, design_var='res_3_l', mode1='Resonator3',
                            tol=30e6)
        designer.add_target(target_type='transmon_freq', target_val=3.5e9, design_var='LJ_3', mode1='Transmon3', tol=30e6)
        designer.add_target(target_type='alpha', target_val=170e6, design_var='qb_3_pad_l', mode1='Transmon3', tol=10e6)
        designer.add_target(target_type='chi', target_val=3e6, design_var='readgap_3', mode1='Resonator3',
                            mode2='Transmon3',
                            tol=0.5e6, speed=0.4)

        # designer.add_target(target_type='kappa', target_val=2e6, design_var='res_port_z', mode1='Resonator',
        #                     tol=0.4e6, speed=0.4)

        designer.add_WISPE_target(design_var='CS_x3', mode1='Transmon3', cutoff=4e7, units='mm', guess_step=0.5)

    if chip_num == 4:
        designer = TubeDesigner(r'D:\Ansoft', r'mega_demo_5', r'tube4')

        designer.add_resonator('Resonator4', 'res4')

        designer.add_transmon('Transmon4', 'transmon_4', 'LJ_4', 'junc4', 'Polyline4')

        designer.add_target(target_type='resonator_freq', target_val=5.65e9, design_var='res_4_l', mode1='Resonator4',
                            tol=30e6)
        designer.add_target(target_type='transmon_freq', target_val=3.6e9, design_var='LJ_4', mode1='Transmon4', tol=30e6)
        designer.add_target(target_type='alpha', target_val=170e6, design_var='qb_4_pad_l', mode1='Transmon4', tol=10e6)
        designer.add_target(target_type='chi', target_val=4e6, design_var='readgap_4', mode1='Resonator4',
                            mode2='Transmon4',
                            tol=0.5e6, speed=0.4)

        # designer.add_target(target_type='kappa', target_val=2e6, design_var='res_port_z', mode1='Resonator',
        #                     tol=0.4e6, speed=0.4)

        designer.add_WISPE_target(design_var='CS_x4', mode1='Transmon4', cutoff=4e7, units='mm', guess_step=0.5)



    designer.init_EPR()
    designer.iterate_loop(max_num=30)

