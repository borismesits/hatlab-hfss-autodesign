from pyaedt import Hfss
import numpy as np
import pyEPR as epr

class TubeDesigner():
    def __init__(self, project_path, project_name, design_name, version=None, new_session=False):
        self.project_path = project_path
        self.project_name = project_name
        self.design_name = design_name

        self.hfss_instance= Hfss(project_name, design_name, new_desktop_session=new_session)

        self.targets = []

        self.objects_dict = {}

        # This dictionary list can be populated with self.define_mode.
        # Each dict has a name, so you can define couplings between, say, qubit 1 and resonator 1.
        # It also has the name of a 2D object that must be defined in HFSS - this makes it possible to
        # link each eigenmode to a spatial object, based on where the fields live.
        self.modes = []

        self.eprd = None

    def add_qb_freq_target(self, type, target_val, design_var, mode1, mode2=None, unit='mm'):

        target_dict = {
            'type': type,
            'target_val': target_val,
            'design_var': design_var,
            'mode1': mode1,
            'mode2': mode2,
            'unit': unit
        }

        self.targets.append(target_dict)

    def add_linear_object(self, objects_dict, name, sheet_name):

        object_properties_dict = {}

        object_properties_dict['mode_index'] = -1
        object_properties_dict['sheet'] = sheet_name
        object_properties_dict['type'] = 'linear'

        objects_dict[name] = object_properties_dict

    def add_nonlinear_object(self, objects_dict, name, sheet_name, jj_var, jj_rect, jj_line):

        object_properties_dict = {}

        object_properties_dict['mode_index'] = -1
        object_properties_dict['sheet'] = sheet_name
        object_properties_dict['jj_var'] = jj_var
        object_properties_dict['jj_rect'] = jj_rect
        object_properties_dict['jj_line'] = jj_line
        object_properties_dict['type'] = 'nonlinear'

        objects_dict[name] = object_properties_dict

    def assign_mode_indices(self):

        num_modes = int(self.eprd.setup.n_modes)

        object_mode_matrix = np.zeros([num_modes, len(self.objects_dict)])

        for j in range(0, num_modes):

            print(j)

            self.eprd.set_mode(j)

            norm = self.eprd.calc_energy_electric()

            for i, key in enumerate(self.objects_dict):
                object_mode_matrix[j, i] = self.eprd.calc_energy_electric(obj=self.objects_dict[key]['sheet'], obj_dims=2,
                                                                     smooth=True) / norm

        # done in a separate loop to avoid unecessary calls of eprd.calc_energy_electric()
        for i, key in enumerate(self.objects_dict):
            matrix_column = object_mode_matrix[:, i]

            mode_index = np.where(matrix_column == np.max(matrix_column))

            self.objects_dict[key]['mode_index'] = int(mode_index[0])


    def get_iteration_results(self):
        pass

    def init_EPR(self):

        savedir = self.project_path

        self.pinfo = epr.ProjectInfo(project_path=self.project_path, project_name=self.project_name,
                                design_name=self.design_name)

        for i, key in enumerate(self.objects_dict):

            if self.objects_dict[key]['type'] == 'nonlinear':
                jj_var = self.objects_dict[key]['jj_var']
                jj_rect = self.objects_dict[key]['jj_rect']
                jj_line = self.objects_dict[key]['jj_line']
                self.pinfo.junctions[self.objects_dict[key]] = {'Lj_variable': jj_var, 'rect': jj_rect, 'line': jj_line}

        self.pinfo.validate_junction_info()

    def run_EPR(self):

        eprd = epr.DistributedAnalysis(self.pinfo)
        # if 1:
        # eprd.hfss_report_full_convergence() # report convergence
        eprd.do_EPR_analysis(append_analysis=False,
                             variations=str(eprd.variations[-1]))  # calculate energy participation ratio


        self.eprd = eprd


    def update_design_vars(self):

        for target_dict in self.targets:

            current_var = self.hfss_instance[target_dict['design_var']]


    def iterate(self):

        hfss.analyze()

        self.get_iteration_results()

        self.update_design_vars()


if __name__ == '__main__':

    designer = TubeDesigner(r'C:/Users/hatlab-boris/Documents/ANSYS/',r'panflute_israa',r'optimizer_test')
    designer.init_EPR()




