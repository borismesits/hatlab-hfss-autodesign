from pyaedt import Hfss
import numpy as np
import pyEPR as epr
import pandas as pd
import tube_physics
from designer import TubeDesigner

if __name__ == '__main__':

    designer = TubeDesigner(r'C:/Users/hatlab-boris/Documents/ANSYS/', r'panflute_israa', r'optimizer_test1')

    designer.add_resonator('Resonator', 'resonator')

    designer.add_transmon('Transmon', 'transmon', 'Lq', 'island', 'Polyline1')

    designer.add_target(target_type='resonator_freq', target_val=7e9, design_var='resonatorL', mode1='Resonator',
                        tol=50e6)
    designer.add_target(target_type='transmon_freq', target_val=5e9, design_var='Lq', mode1='Transmon', tol=50e6)
    designer.add_target(target_type='alpha', target_val=200e6, design_var='AntennaL', mode1='Transmon', tol=10e6)
    designer.add_target(target_type='chi', target_val=2e6, design_var='gap', mode1='Resonator', mode2='Transmon',
                        tol=0.4e6, speed=0.4)

    designer.add_target(target_type='kappa', target_val=2e6, design_var='res_port_z', mode1='Resonator',
                        tol=0.4e6, speed=0.4)

    designer.add_WISPE_target(design_var='wispeX', mode1='Transmon', cutoff=4e8, units='mm', guess_step=0.5)

    designer.init_EPR()
    designer.iterate_loop(max_num=8)

