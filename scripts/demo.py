from pyaedt import Hfss
import numpy as np
import pyEPR as epr
import pandas as pd
import tube_physics
from designer import TubeDesigner

if __name__ == '__main__':

    designer = TubeDesigner(r'C:/Users/hatlab-boris/Documents/ANSYS/', r'panflute_israa', r'optimizer_test1')

    designer.add_resonator('Resonator', 'resonator')

    designer.add_target(target_type='resonator_freq', target_val=7e9, design_var='resonatorL', mode1='Resonator', tol=10e6)

    designer.init_EPR()
    designer.iterate_loop()





