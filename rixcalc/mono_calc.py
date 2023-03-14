"""
Calculation for Linear Dispersion of the Mono in the exit slit plane
"""
import numpy as np
import time
import os
import math

import logging
logger = logging.getLogger(__name__)

def calc_beta(photon_energy,diff_order,groove_density,grating_inc_angle):
    numerator = -(diff_order) * (1239.852 / photon_energy) * (groove_density / 1000000)
    radian = math.radians(grating_inc_angle)
    sin_radian = math.sin(radian)
    result = numerator + sin_radian
    if result < 1:
        Beta = math.degrees(math.asin(result))
        return Beta
    else:
        return 0

def calc_bragg(photon_energy, diff_order,d1):
    d1_Bragg = diff_order * (1239.852 / (photon_energy * 1000000)) * d1
    return d1_Bragg

def calc_r_prime(photon_energy,diff_order,groove_density,grating_inc_angle,d1,virt_source_dist,rad_curv):
    beta = calc_beta(photon_energy,diff_order,groove_density,grating_inc_angle)
    d1_Bragg = calc_bragg(photon_energy, diff_order,d1)
    if beta > 0:
        cos_grating_inc_angle = math.cos(math.radians(grating_inc_angle))
        cos_Beta = math.cos(math.radians(beta))
        numerator = cos_Beta**2
        denominator = (d1_Bragg - ((cos_grating_inc_angle**2) / virt_source_dist) + (cos_grating_inc_angle / rad_curv) + (cos_Beta / rad_curv))
        R_prime =  numerator / denominator
        return R_prime
    else:
        return 0

def calc_lambda(photon_energy):
    lambda_calc = (1239.842 / (photon_energy * 1000000)) * (10**-3)
    return lambda_calc


def get_lin_disp(photon_energy):
    '''
    Calculates the reciprocal linear dispersion of the monochromator through the exit slit plane
    Arguments: The photon energy of the beam
    Returns: The reciprocal linear dispersion
    '''

    # Constants
    groove_density = 50 # Groove density (l/mm)
    diff_order = 1 # Diffraction order
    d1 = -0.0244 # Grating constant?
    grating_inc_angle = 88.627325 # Incidence angle grating (deg)
    virt_source_dist = -7540.0458 # Virtual source distance from grating (mm)
    rad_curv = 9*(10**99) # Radius of curvature (mm)

    Beta = calc_beta(photon_energy,diff_order,groove_density,grating_inc_angle)
    Lambda = calc_lambda(photon_energy)
    R_Prime = calc_r_prime(photon_energy,diff_order,groove_density,grating_inc_angle,d1,virt_source_dist,rad_curv)

    # Actual calculation
    a = math.cos(math.radians(Beta))
    b =  groove_density * diff_order * R_Prime
    c = photon_energy / (Lambda * (10**9))
    linear_disp = (a / b) * c * 1000000
    return linear_disp

