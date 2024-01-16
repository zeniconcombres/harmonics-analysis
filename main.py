"""The following script runs harmonic analysis using the functions in this repository.

Created by: Inez Zheng (@zeniconcombres)
Created on: 11/12/23
"""

from background_harmonics import *
from plotter import *
import pandas as pd 
from pandas import DataFrame as df

#### INPUTS ####
x_h = 30.0 # Ohms
r_h = 100.0 # Ohms
v_bkg_h = 0.75 # %
h = 14 # th order harmonic

# Network impedance range to be scanned across
x_range = [-1000,1000]
r_range = [0,1000]
step = 1.0

# Plots
filename = 'amplification_plot'
plot_figure = True

########## CALCULATING THE BACKGROUND HARMONICS ##########
R, X, R_range, X_range = gen_soln_space(xspan=r_range, yspan=x_range, step=step)
AF = calc_amplification(x_h=450.0, r_h=80.0, v_bkg_h=0.75, R=R, X=X, h=11)

# x_list = AF[:,[i[0] for i in enumerate(R_range) if i[1]==r_h]]
# print(x_list.transpose()[0])
# print(len(x_list))

# r_list = AF[[i[0] for i in enumerate(X_range) if i[1]==x_h]][0]
# print(r_list)
# print(len(r_list))
# ampfac_df = df(AF, index=[X_range.flatten()], columns=[R_range.flatten()])
# ampfac_df.index = [int(i[0]) for i in ampfac_df.index.values]
# ampfac_df.columns = [int(i[0]) for i in ampfac_df.columns.values]

# print(ampfac_df.head())
# print(ampfac_df[[r_h]])
# print(ampfac_df.transpose()[[x_h]])

########### PLOTTING THE RESULTS ##################
plot_soln_space(
    R_range, X_range, AF,
    site_r=r_h, site_x=x_h, r_h=r_h, x_h=x_h, h=h,
    polygon=None, # TODO!!! 
    filename=filename+'_{:02d}'.format(h)
) if plot_figure else None