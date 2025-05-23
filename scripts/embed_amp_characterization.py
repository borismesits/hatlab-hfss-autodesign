from pyaedt import Hfss
import numpy as np
import pyEPR as epr
import pandas as pd
import tube_physics
from designer import TubeDesigner

if __name__ == '__main__':

    designer = TubeDesigner(r'D:\Ansoft', r'Embedded Amp 2025', r'EA_cooldown20241106',updateDesignOn=False)


    designer.add_resonator('res1', 'res1')
    designer.add_resonator('res2', 'res2')
    designer.add_resonator('res3', 'res3')
    designer.add_resonator('res4', 'res4')

    designer.add_transmon('qb1', 'qb1', 'Lj_1', 'junc_qb1', 'line_qb1')
    designer.add_transmon('qb2', 'qb2', 'Lj_2', 'junc_qb2', 'line_qb2')
    designer.add_transmon('qb3', 'qb3', 'Lj_3', 'junc_qb3', 'line_qb3')
    designer.add_SNAIL('SNAIL', 'snail', 'Lj_snail', 'junc_snail', 'line_snail', snail_alpha=0.25, snail_n=2, snail_m=1)

    designer.init_EPR()
    designer.run_EPR()




