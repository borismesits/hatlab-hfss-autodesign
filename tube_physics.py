import numpy as np

Phi_0 = 2.067e-15

def update_res_l(omega_old, omega_new, res_l_old):
     return res_l_old*omega_old/omega_new

def update_Lj(omega_old, omega_new, alpha_old, alpha_new, Lj_old):

     numerator = 2*alpha_new*(Phi_0/np.pi)**2

     denominator = ( ( Phi_0 / np.pi * np.sqrt(2 * alpha_old / Lj_old) - alpha_old) * omega_new / omega_old - alpha_new)**2

     return numerator/denominator

def update_Lj_simple(omega_old, omega_new, Lj_old):

     return Lj_old*(omega_old/omega_new)**2

def update_gap(chi_old, chi_new, gap_old):
     return gap_old*chi_old/chi_new

def update_pin_z(Q_old, Q_new, pin_z_old):
     return pin_z_old + np.log(Q_old/Q_new)

def update_qb_pad_l(alpha_old, alpha_new, pad_l_old):
     return pad_l_old*alpha_old/alpha_new

def update_g3(mode, length, target):
     pass

def update_g2eff(mode, length, target):
     pass