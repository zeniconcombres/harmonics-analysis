"""The following script runs harmonic analysis using the functions in this repository.

Created by: Inez Zheng (@zeniconcombres)
Created on: 11/12/23
"""

from background_harmonics import *

#### INPUTS ####
x_h = 30.0 # Ohms
r_h = 100.0 # Ohms
v_bkg_h = 0.75 # %
h = 11 # th order harmonic

# Network impedance range to be scanned across
x_range = [-1000,1000]
r_range = [0,1000]
step = 1.0

# Plots
filename = 'amplification_plot'
plot_figure = True

########## CALCULATING THE BACKGROUND HARMONICS ##########
R, X, R_range, X_range = gen_soln_space(xspan=r_range, yspan=x_range, step=step)
AF = calc_amplification(x_h=30.0, r_h=100.0, v_bkg_h=0.75, R=R, X=X, h=11) 

# plotting the results
plot_soln_space(
    R_range, X_range, AF,
    r_h, x_h, h,
    filename=filename+'_{:02d}'.format(h)
) if plot_figure else None