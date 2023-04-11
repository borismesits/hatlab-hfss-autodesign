from pyaedt import Hfss
import numpy as np
import pyEPR as epr
import pandas as pd
import tube_physics
import snail_physics
from wispe_optimizer import WISPE_next_guess
from contextlib import redirect_stdout
import io

class TubeDesigner():
    def __init__(self, project_path, project_name, design_name, version=None, new_session=False):
        self.project_path = project_path
        self.project_name = project_name
        self.design_name = design_name

        self.hfss_instance = Hfss(project_name, design_name, new_desktop_session=new_session)

        self.targets = []
        self.WISPE_targets = []

        self.objects_dict = {}

        # This dictionary list can be populated with self.define_mode.
        # Each dict has a name, so you can define couplings between, say, qubit 1 and resonator 1.
        # It also has the name of a 2D object that must be defined in HFSS - this makes it possible to
        # link each eigenmode to a spatial object, based on where the fields live.
        self.modes = []

        self.eprd = None
        self.epra = None
        self.epra_results = None

        self.status = 0  # whether the optimizer is finished. 0 means no, 1 means yes, -1 means something broke.
        self.WISPE_status = 0  # whether the WISPE subroutine is done

        self.num_jjs = 0

    def add_target(self, target_type=None, target_val=None, design_var=None, mode1=None, mode2=None,
                   tol=None, units=None, speed=1):

        target_dict = {
            'target_type': target_type,
            'target_val': target_val,
            'design_var': design_var,
            'mode1': mode1,
            'mode2': mode2,
            'tol': tol,
            'units': units,
            'design_val_history': np.array([]),
            'target_val_history': np.array([]),
            'speed': speed
        }

        self.targets.append(target_dict)

    def add_WISPE_target(self, design_var=None, mode1=None, cutoff=1e9, units='mm', guess_step=1):

        WISPE_target_dict = {

            'design_var': design_var,
            'mode1': mode1,
            'units': units,
            'cutoff': cutoff,
            'design_val_history': np.array([]),
            'target_val_history': np.array([]),
            'guess_step': guess_step
        }

        self.WISPE_targets.append(WISPE_target_dict)

    def add_resonator(self, name, sheet_name):

        object_properties_dict = {}

        object_properties_dict['mode_index'] = -1
        object_properties_dict['sheet'] = sheet_name
        object_properties_dict['type'] = 'resonator'

        self.objects_dict[name] = object_properties_dict

    def add_transmon(self, name, sheet_name, jj_var, jj_rect, jj_line, snail_alpha=None, snail_n=None, snail_m=None):

        object_properties_dict = {}

        object_properties_dict['mode_index'] = -1
        object_properties_dict['sheet'] = sheet_name
        object_properties_dict['jj_var'] = jj_var
        object_properties_dict['jj_rect'] = jj_rect
        object_properties_dict['jj_line'] = jj_line
        object_properties_dict['type'] = 'nonlinear'
        object_properties_dict['jj_index'] = self.num_jjs

        self.num_jjs += 1

        self.objects_dict[name] = object_properties_dict

    def add_SNAIL(self, name, sheet_name, jj_var, jj_rect, jj_line, snail_alpha, snail_n, snail_m):
        object_properties_dict = {}

        object_properties_dict['mode_index'] = -1
        object_properties_dict['sheet'] = sheet_name
        object_properties_dict['jj_var'] = jj_var
        object_properties_dict['jj_rect'] = jj_rect
        object_properties_dict['jj_line'] = jj_line
        object_properties_dict['type'] = 'nonlinear'
        object_properties_dict['snail_alpha'] = snail_alpha
        object_properties_dict['snail_n'] = snail_n
        object_properties_dict['snail_m'] = snail_m
        object_properties_dict['jj_index'] = self.num_jjs

        self.num_jjs += 1

        self.objects_dict[name] = object_properties_dict

    def assign_mode_indices(self):

        print('Assigning mode indices...')

        num_modes = int(self.eprd.setup.n_modes)

        object_mode_matrix = np.zeros([num_modes, len(self.objects_dict)])

        for j in range(0, num_modes):

            self.eprd.set_mode(j)

            norm = self.eprd.calc_energy_electric()

            for i, key in enumerate(self.objects_dict):
                object_mode_matrix[j, i] = self.eprd.calc_energy_electric(obj=self.objects_dict[key]['sheet'],
                                                                          obj_dims=2,
                                                                          smooth=True) / norm

        # done in a separate loop to avoid unecessary calls of eprd.calc_energy_electric()
        for i, key in enumerate(self.objects_dict):
            matrix_column = object_mode_matrix[:, i]

            mode_index = np.where(matrix_column == np.max(matrix_column))

            self.objects_dict[key]['mode_index'] = int(mode_index[0])

        print('Mode matrix: ')
        print(object_mode_matrix)
        print('...done!')

        self.object_mode_matrix = object_mode_matrix

        return object_mode_matrix

    def init_EPR(self):

        print('Setting up pyEPR...')

        savedir = self.project_path

        self.pinfo = epr.ProjectInfo(project_path=self.project_path, project_name=self.project_name,
                                     design_name=self.design_name)

        for i, key in enumerate(self.objects_dict):

            if self.objects_dict[key]['type'] == 'nonlinear':
                jj_var = self.objects_dict[key]['jj_var']
                jj_rect = self.objects_dict[key]['jj_rect']
                jj_line = self.objects_dict[key]['jj_line']
                self.pinfo.junctions[key] = {'Lj_variable': jj_var, 'rect': jj_rect, 'line': jj_line}

        self.pinfo.validate_junction_info()

        print('...done!')

    def run_EPR(self):

        print('Running pyEPR...')

        with redirect_stdout(io.StringIO()) as f:
            eprd = epr.DistributedAnalysis(self.pinfo)
            # if 1:
            # eprd.hfss_report_full_convergence() # report convergence
            eprd.do_EPR_analysis(append_analysis=False,
                                 variations=str(eprd.variations[-1]))  # calculate energy participation ratio

            epra = epr.QuantumAnalysis(eprd.data_filename, variations=str(eprd.variations[-1]))

            epra_results = epra.analyze_variation(variation=str(eprd.variations[-1]), print_result=False)

            self.eprd = eprd
            self.epra = epra
            self.epra_results = epra_results

        print('...done!')

    def update_design_vars(self):

        self.status = 1

        for target_dict in self.targets:

            mode1_index = self.objects_dict[target_dict['mode1']]['mode_index']
            mode2_index = None
            try:
                mode2_index = self.objects_dict[target_dict['mode2']]['mode_index']
            except:
                pass
            tv_old = None
            tv_new = target_dict['target_val']
            physics_function = None

            if target_dict['target_type'] == 'transmon_freq':
                tv_old = self.epra_results['f_0'][mode1_index] * 1e6
                physics_function = tube_physics.update_Lj_simple
                tv_unit = 'GHz'
                dv_unit = 'nH'
                tv_factor = 1e9

            if target_dict['target_type'] == 'SNAIL_freq':
                # currently the same as transmon freq, but this is a bad approximation, so solver needs low speed here
                tv_old = self.epra_results['f_0'][mode1_index] * 1e6
                physics_function = tube_physics.update_qb_pad_l
                tv_unit = 'GHz'
                dv_unit = 'mm'
                tv_factor = 1e9

            if target_dict['target_type'] == 'resonator_freq':
                tv_old = self.epra_results['f_0'][mode1_index] * 1e6
                physics_function = tube_physics.update_res_l
                tv_unit = 'GHz'
                dv_unit = 'mm'
                tv_factor = 1e9

            if target_dict['target_type'] == 'chi':
                tv_old = self.epra_results['chi_O1'][mode1_index][mode2_index] * 1e6
                physics_function = tube_physics.update_gap
                tv_unit = 'MHz'
                dv_unit = 'mm'
                tv_factor = 1e6

            if target_dict['target_type'] == 'alpha':
                tv_old = self.epra_results['chi_O1'][mode1_index][mode1_index] * 1e6
                physics_function = tube_physics.update_qb_pad_l
                tv_unit = 'MHz'
                dv_unit = 'mm'
                tv_factor = 1e6

            if target_dict['target_type'] == 'snail_g3':
                jjsnail_index = self.objects_dict[target_dict['mode1']]['jj_index']

                ZPF = self.epra_results['ZPF'][mode1_index, jjsnail_index]

                jj_var = self.objects_dict[target_dict['mode1']]['jj_var']
                Lj = float(self.hfss_instance[jj_var][:-2])

                snail_alpha = self.objects_dict[target_dict['mode1']]['snail_alpha']
                snail_n = self.objects_dict[target_dict['mode1']]['snail_n']
                snail_m = self.objects_dict[target_dict['mode1']]['snail_m']

                snail = snail_physics.SNAIL(Lsim=Lj / 1e9, alpha=snail_alpha, n=snail_n, m=snail_m)
                c3max = snail.c3max
                tv_old = np.abs(snail_physics.g_n(c3max, [ZPF, ZPF, ZPF]))

                physics_function = tube_physics.update_Lj_simple
                tv_unit = 'MHz'
                dv_unit = 'nH'
                tv_factor = 1e6

            if target_dict['target_type'] == 'g2eff':
                jjsnail_index = self.objects_dict[target_dict['mode1']]['jj_index']
                jjmode_index = self.objects_dict[target_dict['mode1']]['jj_index']

                ZPFsnail = self.epra_results['ZPF'][mode1_index, jjsnail_index]
                ZPFmode = self.epra_results['ZPF'][mode2_index, jjmode_index]

                jj_var = self.objects_dict[target_dict['mode1']]['jj_var']
                Lj = float(self.hfss_instance[jj_var][:-2])

                snail_alpha = self.objects_dict[target_dict['mode1']]['snail_alpha']
                snail_n = self.objects_dict[target_dict['mode1']]['snail_n']
                snail_m = self.objects_dict[target_dict['mode1']]['snail_m']

                snail = snail_physics.SNAIL(Lsim=Lj/1e9, alpha=snail_alpha, n=snail_n, m=snail_m)
                c3max = snail.c3max
                tv_old = np.abs(snail_physics.g_n(c3max, [ZPFsnail, ZPFsnail, ZPFmode]))

                physics_function = tube_physics.update_gap
                tv_unit = 'MHz'
                dv_unit = 'mm'
                tv_factor = 1e6

            if target_dict['target_type'] == 'kappa':
                tv_old = self.epra_results['f_0'][mode1_index]/self.epra_results['Qs'][mode1_index] * 1e6
                physics_function = tube_physics.update_pin_z
                tv_unit = 'MHz'
                dv_unit = 'mm'
                tv_factor = 1e6

            error = np.abs(tv_old - tv_new) / tv_old
            dv_old = float(self.hfss_instance[target_dict['design_var']][:-2])

            target_dict['target_val_history'] = np.append(target_dict['target_val_history'], tv_old)
            target_dict['design_val_history'] = np.append(target_dict['design_val_history'], dv_old)

            mode_string = ''
            if mode2_index is None:
                mode_string = 'For ' + target_dict['target_type'] + ' of ' + target_dict['mode1']
            else:
                mode_string = 'For ' + target_dict['target_type'] + ' of ' + target_dict['mode1'] + ' and' + target_dict['mode2']
            if error > 1e3:
                self.status = -1
                return

            elif np.abs(tv_old - tv_new) > target_dict['tol']:
                self.status = 0
                self.WISPE_status = 0

                dv_new = physics_function(tv_old, tv_new, dv_old)

                speed = target_dict['speed']

                dv_new = speed*dv_new + (1-speed)*dv_old

                self.hfss_instance[target_dict['design_var']] = str(dv_new) + dv_unit
                print(
                    mode_string + ', to make %.3f %s into %.3f %s, %s was changed from %.3f %s to %.3f %s.' % (
                        tv_old / tv_factor, tv_unit, tv_new / tv_factor, tv_unit, target_dict['design_var'], dv_old,
                        dv_unit, dv_new, dv_unit))
            else:
                print(
                    mode_string + ', %.3f %s is within tolerance of %.4f %s, %s was left at %.3f %s.' % (
                        tv_old / tv_factor, tv_unit, target_dict['tol'] / tv_factor, tv_unit, target_dict['design_var'],
                        dv_old, dv_unit))

        if self.status == 1:
            if self.WISPE_status == 0:

                print('Starting WISPE loop...')

                for WISPE_target_dict in self.WISPE_targets:

                    self.WISPE_loop(WISPE_target_dict)

                self.status = 0
                self.WISPE_status = 1


    def WISPE_loop(self, WISPE_target_dict):

        cutoff = WISPE_target_dict['cutoff']

        guess_step = WISPE_target_dict['guess_step']

        mode1_index = self.objects_dict[WISPE_target_dict['mode1']]['mode_index']

        with redirect_stdout(io.StringIO()) as f:
            port_pos_0 = float(self.hfss_instance[WISPE_target_dict['design_var']][:-2])

            my_data = self.hfss_instance.post.get_solution_data(expressions='Q(' + str(mode1_index+1) + ')')
            Q_current = list(my_data._solutions_mag['Q(' + str(mode1_index+1) + ')'].values())[0]

        port_pos_list = np.array([port_pos_0])
        Q_list = np.array([Q_current])

        mode_string = 'For WISPE of ' + WISPE_target_dict['mode1']
        print(mode_string + ', Q is starting at %.3f million, with port position %.3f.' % (
            Q_current / 1e6, port_pos_0))

        counter = 0

        while (np.max(Q_list) < cutoff):

            port_pos_guess = WISPE_next_guess(port_pos_list, Q_list, guess_step=guess_step)

            port_pos_list = np.append(port_pos_list, port_pos_guess)

            with redirect_stdout(io.StringIO()) as f:
                self.hfss_instance[WISPE_target_dict['design_var']] = str(port_pos_guess) + 'mm'

            self.analyze_HFSS()

            with redirect_stdout(io.StringIO()) as f:
                my_data = self.hfss_instance.post.get_solution_data(expressions='Q(' + str(mode1_index+1) + ')')
                Q_current = list(my_data._solutions_mag['Q(' + str(mode1_index+1) + ')'].values())[0]

            Q_list = np.append(Q_list, Q_current)

            mode_string = 'For WISPE of ' + WISPE_target_dict['mode1']

            print(mode_string + ', Q is now %.3f million, with port position %.3f.' % (
                    Q_current/1e6, port_pos_guess))

            counter += 1

            if (counter == 10):
                break

        best_index = np.where(Q_list == np.max(Q_list))
        with redirect_stdout(io.StringIO()) as f:
            self.hfss_instance[WISPE_target_dict['design_var']] = str(port_pos_list[best_index][0]) + 'mm'

        print('...finished WISPE loop!')

        np.append(WISPE_target_dict['target_val_history'], port_pos_list[best_index])
        np.append(WISPE_target_dict['design_val_history'], port_pos_list[best_index])

    def analyze_HFSS(self):

        print('Running HFSS analysis...')
        try:
            with redirect_stdout(io.StringIO()) as f:
                self.hfss_instance.analyze()
        except:
            print('HFSS analysis failed.')

        print('...done!')

    def iterate_loop(self, max_num=100):


        self.analyze_HFSS() # Solve current design (will skip if already solved)
        self.run_EPR() # calculate all the frequencies, shifts, etc we are designing for
        self.assign_mode_indices()

        counter = 0

        while True:

            self.update_design_vars()

            if self.status == 1:
                print('Optimizer finished!')
                break

            elif self.status == -1:
                raise Exception('Relative error very high, perhaps optimizer not stable!')
                break

            self.hfss_instance.cleanup_solution()
            self.analyze_HFSS()
            self.run_EPR()
            self.assign_mode_indices()

            counter += 1

            if counter == max_num:
                break

if __name__ == '__main__':

    pass




