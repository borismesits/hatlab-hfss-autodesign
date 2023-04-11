# -*- coding: utf-8 -*-
"""
Created on Mon Dec 06 19:48:03 2021

@author: Chao
"""
import csv
import re
from typing import List
from functools import partial
import warnings

import numpy as np
import scipy as sp
from scipy.optimize import fsolve
from scipy.optimize import root as FindRoot
from scipy.interpolate import interp1d
import matplotlib.pyplot as plt
from sympy import symbols, diff
import sympy as sym
from sympy.utilities.lambdify import lambdify

PI = np.pi
e = sp.constants.e
hbar = sp.constants.hbar
phi0 = hbar / (2 * e)


class SNAIL:
    def __init__(self, Lsim, alpha, n=3, m=1):
        """

        :param Lsim: The SNAIL linear inductance in HFSS simulation, represents the total SNAIL
            linear inductance at the kerr-free bias
        :param alpha: Lj_Large/Lj_Small
        :param n: number of junctions on the large junction side
        :param m: number of SNAILs in series
        """
        self.Lsim = Lsim
        self.alpha = alpha
        self.n = n
        self.m = m
        self.modulation_done = False
        self.solveForNullPoint()

    # coefficients C1 to C4 are written down explicitly to speed up calculation. Higher order
    # coefficients can be calculated using self.expansionCoeff()
    def __C1(self, phi_min, phi_ext, EjL):
        return EjL * (self.alpha * np.sin(phi_min / self.m) -
                      np.sin((-phi_min / self.m + phi_ext) / self.n))

    def __C2(self, phi_min, phi_ext, EjL):
        return EjL / 2 / self.m * (self.alpha * np.cos(phi_min / self.m) +
                                   np.cos((-phi_min / self.m + phi_ext) / self.n)/self.n)

    def __C3(self, phi_min, phi_ext, EjL):
        return EjL / 6 / self.m ** 2 * (-self.alpha * np.sin(phi_min / self.m) +
                                        np.sin((-phi_min / self.m + phi_ext) / self.n) / self.n ** 2)

    def __C4(self, phi_min, phi_ext, EjL):
        return EjL / 24 / self.m ** 3 * (-self.alpha * np.cos(phi_min / self.m) -
                                        np.cos((-phi_min / self.m + phi_ext) / self.n) / self.n ** 3)


    def expansionCoeff(self, phi_min, phi_ext, EjL, order):
        Ej_, alpha_, phi_ext_, phi_, n_, m_ = symbols('Ej_ alpha_ phi_ext_ phi_ n_ m_', real=True)
        H_ = m_ * (- alpha_ * Ej_ * sym.cos(phi_ / m_) -
                   n_ * Ej_ * sym.cos((phi_ext_ - phi_ / m_) / n_))
        Cn = lambdify((Ej_, alpha_, phi_ext_, phi_, n_, m_), diff(H_, phi_, order))
        # print(diff(H_, phi_, order), Cn)
        return Cn(EjL, self.alpha, phi_ext, phi_min, self.n, self.m) / np.math.factorial(order)

    def solveForNullPoint(self):
        def equs(variables):
            (Phi_min, Phi_ext, LjS) = variables
            EjL = phi0 ** 2 / (LjS * self.alpha)
            c1 = self.__C1(Phi_min, Phi_ext, EjL)
            c2 = self.__C2(Phi_min, Phi_ext, EjL) - phi0 ** 2 / (self.Lsim * 2)
            c4 = self.__C4(Phi_min, Phi_ext, EjL)
            return [c1, c2, c4]

        self.null_point = fsolve(equs, np.array([0.2/self.m, 0.5, self.Lsim / self.m]))
        self.I0s = phi0 / self.null_point[2]
        self.I0l = self.I0s / self.alpha
        self.Ljl = phi0/self.I0l
        self.Ljs = phi0/self.I0s
        self.EjS = phi0 ** 2 / self.null_point[2]
        self.EjL = self.EjS / self.alpha
        self.nullFlux = self.null_point[1]

        self.c3max = self.__C3(self.null_point[0], self.null_point[1], self.EjL)
        print("small junction critical current (A): ", self.I0s)
        print("large junction critical current (A): ", self.I0l)
        if self.I0s < 0.4e-7:  # 0.3*0.3 um^2 with current density 0.7 uA/um^2
            warnings.warn("Be careful, I0 is kind of small, may hard to fabricate")
        return self.c3max

    def Modulation(self):
        if not self.modulation_done:
            Phi_ext_List = np.linspace(0, 2 * PI * self.n * self.m + 0.1, 5001)
            Phi_min_List = []
            Phi_min_try = Phi_ext_List[0]
            c1_list = []
            c2_list = []
            c3_list = []
            c4_list = []

            for Phi_ext_1 in Phi_ext_List:
                Phi_min_1 = FindRoot(self.__C1, Phi_min_try, args=(Phi_ext_1, self.EjL)).x[0]
                if self.__C2(Phi_min_1, Phi_ext_1, self.EjL) < 0:
                    Phi_min_1 = \
                        FindRoot(self.__C1, Phi_min_1 + self.n * PI * self.m, args=(Phi_ext_1, self.EjL)).x[0]
                if Phi_min_1 < 0 or Phi_min_1 > self.n * self.m * 2 * PI:
                    Phi_min_1 = Phi_min_1 % (self.n * self.m * 2 * PI)
                Phi_min_try = Phi_min_1
                Phi_min_List.append(Phi_min_1)
                c1_list.append(self.__C1(Phi_min_1, Phi_ext_1, self.EjL))
                c2_list.append(self.__C2(Phi_min_1, Phi_ext_1, self.EjL))
                c3_list.append(self.__C3(Phi_min_1, Phi_ext_1, self.EjL))
                c4_list.append(self.__C4(Phi_min_1, Phi_ext_1, self.EjL))
                # plt.plot(Phi_min_List)
            self.Phi_min_itp = interp1d(Phi_ext_List, Phi_min_List)
            self.c1_itp = interp1d(Phi_ext_List, c1_list)
            self.c2_itp = interp1d(Phi_ext_List, c2_list)
            self.c3_itp = interp1d(Phi_ext_List, c3_list)
            self.c4_itp = interp1d(Phi_ext_List, c4_list)
            self.modulation_done = True

    def c1(self, Phi_ext):
        if not self.modulation_done:
            self.Modulation()
        return self.c1_itp(np.mod(Phi_ext, 2 * self.n * self.m * PI))

    def c2(self, Phi_ext):
        if not self.modulation_done:
            self.Modulation()
        return self.c2_itp(np.mod(Phi_ext, 2 * self.n * self.m * PI))

    def c3(self, Phi_ext):
        if not self.modulation_done:
            self.Modulation()
        return self.c3_itp(np.mod(Phi_ext, 2 * self.n * self.m * PI))

    def c4(self, Phi_ext):
        if not self.modulation_done:
            self.Modulation()
        return self.c4_itp(np.mod(Phi_ext, 2 * self.n * self.m * PI))

    def cn(self, Phi_ext, n):
        if not self.modulation_done:
            self.Modulation()
        phi_min_ = self.Phi_min_itp(np.mod(Phi_ext, 2 * self.n * self.m * PI))
        return self.expansionCoeff(phi_min_, Phi_ext, self.EjL, n)

    def plotCoefficients(self, phi_ext_list):
        plt.figure()
        plt.plot(phi_ext_list, self.c1(phi_ext_list), label='C1')
        plt.plot(phi_ext_list, self.c2(phi_ext_list), label='C2')
        plt.plot(phi_ext_list, self.c3(phi_ext_list), label='C3')
        plt.plot(phi_ext_list, self.c4(phi_ext_list), label='C4')
        plt.xlabel('phi_external')
        plt.ylabel('coefficients (J)')
        plt.legend()

    def freq(self, f_null, Phi_ext, L_lin=0):
        return f_null * np.sqrt((self.L_phi(self.nullFlux) + L_lin) / (self.L_phi(Phi_ext) + L_lin))

    def L_phi(self, Phi_ext):
        return phi0 ** 2 / (self.c2(Phi_ext) * 2)

    def plot_freq(self, f_null, L_lin=0):
        """
        :param f_null: SNAIL frequency at nulling point (frequency in HFSS simulation)
        :param L_lin: SNAIL linear inductance from antenna
        :return:
        """
        phi_ext_list = np.linspace(- self.n * PI, self.n * PI, 2001)
        plt.figure()
        plt.plot(phi_ext_list, self.freq(f_null, phi_ext_list, L_lin))
        plt.plot([phi_ext_list[0], phi_ext_list[-1]], [f_null] * 2)
        plt.title('Freq Modulation')
        plt.xlabel('phi_external')
        plt.ylabel('freq')

# def g_n(coeff, z_effs, geo_coeff=1):  # ===returns coupling in Hz
#     gn = geo_coeff * coeff / (2.0 * PI * hbar)
#     for i in range(len(z_effs)):
#         gn *= np.sqrt(hbar / 2 * z_effs[i]) / phi0
#     return gn

def g_n(coeff, phiZPF_list, geo_coeff=1):  # ===returns coupling in Hz
    gn = geo_coeff * coeff / (2.0 * PI * hbar)
    for phiZPF in phiZPF_list:
        gn *= phiZPF
    return gn