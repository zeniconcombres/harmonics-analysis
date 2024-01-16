"""The script contains functions that calculate the background amplification factor
for a given harmonic order based on given impedance of a site (site_x_h, site_r_h) across an area of 
network impedances (X, R). 

Created by: Inez Zheng (@zeniconcombres)
Created on: 11/12/23
"""

import time
import pandas as pd
import numpy as np
from pandas import DataFrame as df

# CONSTANTS

# FUNCTIONS
def gen_soln_space(xspan=[0,1000], yspan=[-1000,1000], step=1.0):
    # Define the ranges and steps for X and Y
    x_range = np.arange(xspan[0], xspan[1]+1, step)
    y_range = np.arange(yspan[0], yspan[1]+1, step)

    # Generate the meshgrid using np.meshgrid
    X, Y = np.meshgrid(x_range, y_range)
    return X, Y, x_range, y_range

def calc_amplification(site_x_h, site_r_h, R, X, v_bkg_h=None , h=2):
    # calculating the voltage split at each network impedance point
    v_drop_h = (site_r_h+(1j*site_x_h)) / ((site_r_h+R)+1j*(site_x_h+X))
    amp_factor = abs(v_drop_h)
    print(f'The maximum amplification factor for h={h} is {np.max(amp_factor)}.')
    # print(amp_factor)
    return amp_factor

if __name__ == "__main__":
    start_time = time.time()
    # Network impedance range to be scanned across
    x_range = [-1000,1000]
    r_range = [0,1000]
    step = 1.0
    R, X, R_range, X_range = gen_soln_space(xspan=r_range, yspan=x_range, step=step)
    # if considering TG, 0.75% is half of 1.5% from the planning levels
    AF = calc_amplification(site_x_h=30.0, site_r_h=100.0, v_bkg_h=0.75, R=R, X=X, h=14) 
    # plot_soln_space(X,Y)
    runtime = round(time.time() - start_time, 1)
    print(f"Runtime: {runtime}s")
