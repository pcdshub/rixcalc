'''
Helper functions for RIX beamline
K. Kunnus, 11/15/2021

update 07/19/2022:
Reporting read-back values (RBV) of the Epics PVs and better handling of mono drifting
'''
import ophyd
from ophyd.signal import EpicsSignal
from caproto import ChannelData, ChannelType
from caproto.server import AsyncLibraryLayer, PVGroup, pvproperty
from caproto.sync.client import read
import numpy as np
import time
import os

import logging
logger = logging.getLogger(__name__)


# path to the folder with benders calibration files
path_calib = os.getcwd()+'/rixcalc'

# KBs benders PVs
PV_usH = 'MR3K2:KBH:MMS:BEND:US'
PV_dsH = 'MR3K2:KBH:MMS:BEND:DS'
PV_usV = 'MR4K2:KBV:MMS:BEND:US'
PV_dsV = 'MR4K2:KBV:MMS:BEND:DS'

def get_KBs():
    '''
    Displays current focus position from ChemRIXS IP.
    Focus position is calculated based on the KBs benders calibration.
    Arguments: None
    Returns: None
    '''

    # bender tables for MR3K2 and MR4K2
    qH, usH, dsH = np.loadtxt(path_calib+'/MR3K2.txt', unpack=True)
    qV, usV, dsV = np.loadtxt(path_calib+'/MR4K2.txt', unpack=True)
    # ChemRIXS distance from MR3K2 and MR4K2
    dH = 8.8
    dV = 7.3

    try:
        temppv = EpicsSignal(PV_usH+'.RBV')
        usH0 = temppv.get()
        temppv = EpicsSignal(PV_dsH+'.RBV')
        dsH0 = temppv.get()
        temppv = EpicsSignal(PV_usV+'.RBV')
        usV0 = temppv.get()
        temppv = EpicsSignal(PV_dsV+'.RBV')
        dsV0 = temppv.get()
    except:
        logger.info('Failed to read PV')

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

def get_E():
    '''
    Reports current photon energy and Cff for based on current grating and pre-mirror pitch target and RBV.
    Reports the FEL set energy.
    Arguments: none
    Returns:   none
    '''

    PV_pitchG = 'SP1K1:MONO:MMS:G_PI'
    PV_pitchM2 = 'SP1K1:MONO:MMS:M_PI'
    PV_SET1 = 'RIX:USER:MCC:EPHOTK:SET1'

    try:
        temppv = EpicsSignal(PV_pitchG+'.RBV')
        pitchG = temppv.get()
    except:
        logger.info('Failed to read PV: ' + PV_pitchG+'.RBV')
    try:
        temppv = EpicsSignal(PV_pitchG)
        pitchG_target = temppv.get()
    except:
        logger.info('Failed to read PV: ' + PV_pitchG)
    try:
        temppv = EpicsSignal(PV_pitchM2+'.RBV')
        pitchM2 = temppv.get()
    except:
        logger.info('Failed to read PV: ' + PV_pitchM2+'.RBV')
    try:
        temppv = EpicsSignal(PV_pitchM2)
        pitchM2_target = temppv.get()
    except:
        logger.info('Failed to read PV: ' + PV_pitchM2)
    try:
        temppv = EpicsSignal(PV_SET1)
        E_FEL = temppv.get()
    except:
        logger.info('Failed to read PV: ' + PV_SET1)


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
    pG = pitchG_target*1e-6 - offsetG
    pM2 = pitchM2_target*1e-6 - offsetM2
    alpha = np.pi/2 - pG + 2*pM2 - thetaM1
    beta = -np.pi/2 - pG + thetaES
    E_target = m*D0*eVmm/(np.sin(alpha) + np.sin(beta))
    Cff_target = np.cos(beta)/np.cos(alpha)

    return E_target, E, E_FEL

def get_benders(*args):
    '''
    Calculates MR1K1 benders current focus position.
    Focus position is calculated based on the MR1K1 benders calibration.
    Arguments: None
    Returns: None
    '''

    # MR1K1 benders PVs
    PV_us = 'MR1K1:BEND:MMS:US'
    PV_ds = 'MR1K1:BEND:MMS:DS'
    # bender table for MR1K1
    qMR1, usMR1, dsMR1 = np.loadtxt(path_calib+'/MR1K1.txt', unpack=True)

    try:
        temppv = EpicsSignal(PV_us+'.RBV')
        us = temppv.get()
        logger.info('Upstream bender at {0:4.2f} mm'.format(us))
    except:
        logger.info('Failed to read PV: ' + PV_us)
    try:
        temppv = EpicsSignal(PV_ds+'.RBV')
        ds = temppv.get()
        logger.info('Downstream bender at {0:4.2f} mm'.format(ds))
    except:
        logger.info('Failed to read PV: ' + PV_ds)

    q1 = np.interp(us, usMR1, qMR1, left=-1, right=-1)
    q2 = np.interp(ds, dsMR1, qMR1, left=-1, right=-1)
    if q1<0 or q2<0:
        raise Exception('Bender value is out of range.')
    q0 = 0.5*(q1 + q2)
    return q0
