import numpy as np
import time
import os
import pathlib

import logging
logger = logging.getLogger(__name__)

script_directory = pathlib.Path(__file__).resolve().parent

mr1k1_file = script_directory / "MR1K1.txt"
mr3k2_file = script_directory / "MR3K2.txt"
mr4k2_file = script_directory / "MR4K2.txt"

def get_KBs(usH0, dsH0, usV0, dsV0):
    '''
    Displays current focus position from ChemRIXS IP.
    Focus position is calculated based on the KBs benders calibration.
    Arguments: MR3K2 Upstream, MR3K2 Downstream, MR4K2 Upstream, MR4K2 Downstream
    Returns: Upstream and Downstream horizontal focus, Upstream and Downstream vertical focus
    '''

    # bender tables for MR3K2 and MR4K2
    qH, usH, dsH = np.loadtxt(mr3k2_file, unpack=True)
    qV, usV, dsV = np.loadtxt(mr4k2_file, unpack=True)
    # ChemRIXS distance from MR3K2 and MR4K2
    dH = 8.8
    dV = 7.3

    hor0 = np.interp(usH0, usH, qH, left=-1, right=-1)
    hor1 = np.interp(dsH0, dsH, qH, left=-1, right=-1)
    ver0 = np.interp(usV0, usV, qV, left=-1, right=-1)
    ver1 = np.interp(dsV0, dsV, qV, left=-1, right=-1)

    if hor0<0:
        raise Exception('Horizontal KB upstream bender value is out of range.')
    if hor1<0:
        raise Exception('Horizontal KB downstream bender value is out of range.')
    if ver0<0:
        raise Exception('Vertical KB upstream bender value out is of range.')
    if ver1<0:
        raise Exception('Vertical KB downstream bender value is out of range.')

    final_up_h = hor0-dH
    final_ds_h = hor1-dH
    final_up_v = ver0-dV
    final_ds_v = ver1-dV

    return final_up_h, final_ds_h, final_up_v, final_ds_v

def get_E(pitchG, pitchG_target, pitchM2, pitchM2_target):
    '''
    Reports current photon energy and Cff for based on current grating and pre-mirror pitch target and RBV.
    Reports the FEL set energy.
    Arguments: Mono G Pi RBV, Mono G Pi, Mono M Pi RBV, Mono M Pi
    Returns:   Current mono energy, target mono energy
    '''

    # constants
    eVmm = 0.001239842 # Wavelenght[mm] = eVmm/Energy[eV]
    m = 1 # diffraction order
    D0 = 50.0 # 1/mm
    thetaM1 = 0.03662 # rad
    thetaES = 0.1221413 # rad
    offsetM2 = 90641.0e-6 # rad
    offsetG = 63358.0e-6 # rad

    # RBV
    pG = pitchG*1e-6 - offsetG
    pM2 = pitchM2*1e-6 - offsetM2
    alpha = np.pi/2 - pG + 2*pM2 - thetaM1
    beta = -np.pi/2 - pG + thetaES
    E = m*D0*eVmm/(np.sin(alpha) + np.sin(beta))
    Cff = np.cos(beta)/np.cos(alpha)

    # target
    pG_tar = pitchG_target*1e-6 - offsetG
    pM2_tar = pitchM2_target*1e-6 - offsetM2
    alpha_tar = np.pi/2 - pG_tar + 2*pM2_tar - thetaM1
    beta_tar = -np.pi/2 - pG_tar + thetaES
    E_target = m*D0*eVmm/(np.sin(alpha_tar) + np.sin(beta_tar))
    Cff_target = np.cos(beta_tar)/np.cos(alpha_tar)

    return E, E_target

def get_benders(mr1k1_us, mr1k1_ds):
    '''
    Calculates MR1K1 benders current focus position.
    Focus position is calculated based on the MR1K1 benders calibration.
    Arguments: MR1K1 downstream position, MR1K1 upstream position
    Returns: None
    '''

    # bender table for MR1K1
    qMR1, usMR1, dsMR1 = np.loadtxt(mr1k1_file, unpack=True)

    q1 = np.interp(mr1k1_us, usMR1, qMR1, left=-1, right=-1)
    q2 = np.interp(mr1k1_ds, dsMR1, qMR1, left=-1, right=-1)
    if q1<0 or q2<0:
        raise Exception('Bender value is out of range.')
    q0 = 0.5*(q1 + q2)
    return q0
