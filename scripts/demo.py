from pyaedt import Hfss
import numpy as np
import pyEPR as epr
import tube_physics
from designer import TubeDesigner

if __name__ == '__main__':

    designer = TubeDesigner(r'C:/Users/hatlab-boris/Documents/ANSYS/', r'panflute_israa', r'optimizer_test1')

    designer.add_transmon('my transmon', 'transmon', 'Lq', 'island', 'Polyline1')

    designer.add_target(target_type='alpha', target_val=300e6, design_var='AntennaL', mode1='my transmon', tol=10e6)

    designer.init_EPR()
    designer.iterate_loop()





