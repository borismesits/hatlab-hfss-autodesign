#%% converge on freq

from pyaedt import Hfss
import numpy as np
import pyEPR as epr
import pandas as pd

def get_epr_info():
    
    savedir = "C:/Users/hatlab-boris/Documents/Ansoft"
    
    pinfo=epr.ProjectInfo(project_path=r'C:/Users/hatlab-boris/Documents/Ansoft/',project_name=r'Embed_Amp',design_name=r'embed_amp_auto')
    
    pinfo.junctions['SNAIL']={'Lj_variable':'LJsnail','rect':'junc_snail','line':'J_line_snail'}
    pinfo.junctions['qubit1']={'Lj_variable':'LJ1','rect':'junc1','line':'J_line1'}
    pinfo.junctions['qubit3']={'Lj_variable':'LJ2','rect':'junc2','line':'J_line2'}
    pinfo.junctions['qubit4']={'Lj_variable':'LJ3','rect':'junc3','line':'J_line3'}
    pinfo.validate_junction_info()
    #pinfo.setup.analyze()
    
    eprd = epr.DistributedAnalysis(pinfo)
    #if 1:
      #eprd.hfss_report_full_convergence() # report convergence
    eprd.do_EPR_analysis(append_analysis=False, variations=str(eprd.variations[-1])) #calculate energy participation ratio
    
    epra = epr.QuantumAnalysis(eprd.data_filename, variations=str(eprd.variations[-1]))
    # epra.analyze_variation(variation=str(eprd.variations[-1]), print_result=False)
    
    result = epra.analyze_variation(variation=str(eprd.variations[-1]), print_result=False)
    
    dressed_freq = epra.get_frequencies(numeric = True).T
    chi = epra.get_chis(numeric = False)
    hfss_vars = epra._hfss_variables
    
    return result['f_0'][4]*1e6, result['f_0'][5]*1e6, result['f_0'][6]*1e6, result['f_0'][7]*1e6, chi[0][0]*1e6, chi[2][2]*1e6, chi[3][3]*1e6


hfss = Hfss("Embed_Amp", "embed_amp_auto")

post = hfss.post

res1_freq_target = 5.9e9
res2_freq_target = 6.4e9
res3_freq_target = 7.0e9
res4_freq_target = 7.5e9
qb1_alpha_target = 200e6
qb2_alpha_target = 200e6
qb3_alpha_target = 200e6


tol = 1e-4

res1_l_current = float(hfss['res1_l'][:-2])
res2_l_current = float(hfss['res2_l'][:-2])
res3_l_current = float(hfss['res3_l'][:-2])
res4_l_current = float(hfss['res4_l'][:-2])
qb1_pad_current = float(hfss['qb1_pad_1'][:-2])
hfss['qb1_pad_2'] = str(qb1_pad_current)+'mm'
qb2_pad_current = float(hfss['qb2_pad_1'][:-2])
hfss['qb2_pad_2'] = str(qb2_pad_current)+'mm'
qb3_pad_current = float(hfss['qb3_pad_1'][:-2])
hfss['qb3_pad_2'] = str(qb3_pad_current)+'mm'


while(True):
    
    print('Current params')
    print(res1_l_current)
    print(res2_l_current)
    print(res3_l_current)
    print(res4_l_current)
    print(qb1_pad_current)
    print(qb2_pad_current)
    print(qb3_pad_current)
  
    hfss.analyze()
    
    res1_freq_current, res2_freq_current, res3_freq_current, res4_freq_current, qb1_alpha_current, qb2_alpha_current, qb3_alpha_current = get_epr_info()
    
    print('Current values')
    print(res1_freq_current)
    print(res2_freq_current)
    print(res3_freq_current)
    print(res4_freq_current)
    print(qb1_alpha_current)
    print(qb2_alpha_current)
    print(qb3_alpha_current)

    
    res1_l_new = res1_l_current*res1_freq_current/res1_freq_target
    res2_l_new = res2_l_current*res2_freq_current/res2_freq_target
    res3_l_new = res3_l_current*res3_freq_current/res3_freq_target
    res4_l_new = res4_l_current*res4_freq_current/res4_freq_target
    qb1_pad_new = qb1_pad_current*qb1_alpha_target/qb1_alpha_current
    qb2_pad_new = qb2_pad_current*qb2_alpha_target/qb2_alpha_current
    qb3_pad_new = qb3_pad_current*qb3_alpha_target/qb3_alpha_current
    
    
    res1_freq_error = np.abs(res1_freq_current - res1_freq_target)/res1_freq_target
    res2_freq_error = np.abs(res2_freq_current - res2_freq_target)/res2_freq_target
    res3_freq_error = np.abs(res3_freq_current - res3_freq_target)/res3_freq_target
    res4_freq_error = np.abs(res4_freq_current - res4_freq_target)/res4_freq_target
    qb1_alpha_error = np.abs(qb1_alpha_current - qb1_alpha_target)/qb1_alpha_target
    qb2_alpha_error = np.abs(qb2_alpha_current - qb2_alpha_target)/qb2_alpha_target
    qb3_alpha_error = np.abs(qb3_alpha_current - qb3_alpha_target)/qb3_alpha_target
    
    if (qb1_alpha_current < 100e6):
        break
    
    if (qb2_alpha_current < 100e6):
        break
    
    if (qb3_alpha_current < 100e6):
        break
    
    errors = [res1_freq_error,res2_freq_error,res3_freq_error,res4_freq_error,qb1_alpha_error,qb2_alpha_error,qb3_alpha_error]
    
    if np.max(errors) < tol:
        
        break
    
    hfss['res1_l'] = str(res1_l_new)+'mm'
    hfss['res2_l'] = str(res2_l_new)+'mm'
    hfss['res3_l'] = str(res3_l_new)+'mm'
    hfss['res4_l'] = str(res4_l_new)+'mm'
    
    hfss['qb1_pad_1'] = str(qb1_pad_new)+'mm'
    hfss['qb1_pad_2'] = str(qb1_pad_new)+'mm'
    hfss['qb2_pad_1'] = str(qb2_pad_new)+'mm'
    hfss['qb2_pad_2'] = str(qb2_pad_new)+'mm'
    hfss['qb3_pad_1'] = str(qb3_pad_new)+'mm'
    hfss['qb3_pad_2'] = str(qb3_pad_new)+'mm'
    
    
    res1_l_current = res1_l_new
    res2_l_current = res2_l_new
    res3_l_current = res3_l_new
    res4_l_current = res4_l_new
    qb1_pad_current = qb1_pad_new
    qb2_pad_current = qb2_pad_new
    qb3_pad_current = qb3_pad_new
    
    
    post.delete_report()
    
    
 #%% old version

from pyaedt import Hfss
import numpy as np

def WISPE_next_guess(x_list, y_list, guess_step=1):
    
    x_guess = x_list[-1]

    if len(x_list) == 1:
        x_guess = x_list[-1] + guess_step
        
    elif np.where(y_list == np.max(y_list))[0][0] == np.where(x_list == np.min(x_list))[0][0]:
        x_guess = np.min(x_list) - guess_step
        
    elif np.where(y_list == np.max(y_list))[0][0] == np.where(x_list == np.max(x_list))[0][0]:
        x_guess = np.max(x_list) + guess_step
        
    else:
        index_highest = np.argsort(y_list)[-1]
        index_second = np.argsort(y_list)[-2]

        x_guess = (x_list[index_highest] + x_list[index_second])/2
        
    return x_guess

hfss = Hfss("panflute_israa","optimizer_test")

post = hfss.post


x0 = float(hfss['GoodX'][:-2])

hfss.analyze()
my_data = post.get_solution_data(expressions='Q(1)')
Q_current = list(my_data._solutions_mag['Q(1)'].values())[0]

x_list = np.array([x0])
Q_list = np.array([Q_current])
print(x_list)
print(Q_list)


for i in range(0,10):

    x_new = WISPE_next_guess(x_list,Q_list,guess_step=1)    
    hfss['GoodX'] = str(x_new)+'mm'
    
    hfss.analyze()
    my_data = post.get_solution_data(expressions='Q(1)')
    Q_current = list(my_data._solutions_mag['Q(1)'].values())[0]


    x_list = np.append(x_list, x_new)
    Q_list = np.append(Q_list, Q_current)
    print(x_list)
    print(Q_list)
    
#%% old version

from pyaedt import Hfss
import numpy as np
from wispe_optimizer_prototype import WISPE_next_guess

hfss = Hfss("panflute_israa")

post = hfss.post

w_target = 6.5e9

tol = 1e-4

l_current = float(hfss['resonatorL'][:-2])

while(True):
    
    print(l_current)
    
    hfss.analyze()
    
    my_data = post.get_solution_data(expressions='Mode(2)')
    
    w_current = list(my_data._solutions_mag['Mode(2)'].values())[0]
    
    print(w_current)
    
    l_new = l_current*w_current/w_target
    
    rel_error = np.abs(w_current - w_target)/w_target
    
    if rel_error < tol:
        
        break
    
    hfss['resonatorL'] = str(l_new)+'mm'
    
    l_current = l_new
    
    post.delete_report()
    
    
