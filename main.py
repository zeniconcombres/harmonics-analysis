"""The following script runs harmonic analysis using the functions in this repository.

Created by: Inez Zheng (@zeniconcombres)
Created on: 11/12/23
"""


import pandas as pd 
from pandas import DataFrame as df
# reading in all the functions from the specialised scripts 
from background_harmonics import *
from plotter import *
from network_polygons import *

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
# plot_figure = False
plot_figure = True

########## CALCULATING THE BACKGROUND HARMONICS ##########
R, X, R_range, X_range = gen_soln_space(xspan=r_range, yspan=x_range, step=step)
AF = calc_amplification(site_x_h=450.0, site_r_h=80.0, v_bkg_h=0.75, R=R, X=X, h=h)

########### READING IN NETWORK POLYGONS ################
network_polygon_file = 'harmonic_polygons.xlsx'
ibr_project = Project(name="Puffer Fish")
ibr_project.input_network_data(input_filename=network_polygon_file)
print(ibr_project.polygon_data_dict[14].head())
# fig, ax = ibr_project.plot_harmonic_polygon(14)
# fig.savefig("test_polygon.png")

########### PLOTTING THE RESULTS ##################
plot_soln_space(
    R_range, X_range, AF,
    site_r_h=r_h, site_x_h=x_h, plotter_r=r_h, plotter_x=x_h, h=h,
    polygon=ibr_project.polygon_data_dict[h],
    filename=filename+'_{:02d}'.format(h)
) if plot_figure else None