"""The following script runs harmonic analysis using the functions in this repository.

Created by: Inez Zheng (@zeniconcombres)
Created on: 11/12/23
"""

import sys, os
import pandas as pd 
from pandas import DataFrame as df
# reading in all the functions from the specialised scripts 
from background_harmonics import *
from plotter import *
from network_polygons import *

#### WORKING DIRECTORY ####
os.chdir(r"./testing")

#### INPUTS ####
# site impedance
# x_h = 100.0 # Ohms
# r_h = 10.0 # Ohms
x_h = -344.203565 # Ohms
r_h = 42.058105 # Ohms
v_bkg_h = 0.5 # %
h = 14 # th order harmonic

# Network impedance range to be scanned across
x_range = [-1000,1000]
r_range = [0,1000]
step = 1.0

# Plots
filename = 'amplification_plot'
plot_figure = False
print_figure = False
plot_figure = True
print_figure = True

########## CALCULATING THE BACKGROUND HARMONICS ##########
R, X, R_range, X_range = gen_soln_space(xspan=r_range, yspan=x_range, step=step)
AF = calc_amplification(site_x_h=x_h, site_r_h=r_h, v_bkg_h=0.75, R=R, X=X, h=h)

########### READING IN NETWORK POLYGONS ################
network_polygon_file = "test_data.xlsx"
polygon_worksheet = "polygon"
base = 100.0 #MVA
# network_polygon_file = 'harmonic_polygons.xlsx'
ibr_project = Project(name="Puffer Fish")
ibr_project.input_network_data(input_filename=network_polygon_file, input_sheet=polygon_worksheet, base=base)
# showing a single harmonic order polygon that's used as a demo
ibr_h14 = ibr_project.polygon_data_dict[14]
print(ibr_h14.head())
# fig, ax = ibr_project.plot_harmonic_polygon(14)
# fig.savefig("test_polygon.png")

#### calculating network polygon amplification points ######
print("CORNER POINTS")
network_poly_cnr_pt_AF = calc_amplification(
    site_x_h=x_h, site_r_h=r_h, v_bkg_h=0.75, 
    R=ibr_h14['R14'], X=ibr_h14['X14'], h=h
)
# interpolating points between the polygon corner points and calculating AF for these points
print("BOUNDARY SWEEP")
interpolated_pts_14 = ibr_project.interpolate_polygon_points(h, num_pts=100, print_figure=print_figure)
network_poly_boundary_AF = calc_amplification(
    site_x_h=x_h, site_r_h=r_h, v_bkg_h=0.75, 
    R=interpolated_pts_14['R14'], X=interpolated_pts_14['X14'], h=h
)
# print(network_poly_all_AF.tail())
# generating points inside the network polygon and calculating AF for each point inside
print("AREA SWEEP")
h14_points_inside = ibr_project.generate_random_points_inside_polygon(h, print_figure=print_figure)
network_poly_inside_AF = calc_amplification(
    site_x_h=x_h, site_r_h=r_h, v_bkg_h=0.75, 
    R=h14_points_inside['R14'], X=h14_points_inside['X14'], h=h
)
print(f"The 95th percentile AF inside the polygon is: {network_poly_inside_AF.quantile(q=0.95)}")
polygon_data_h14 = pd.concat([h14_points_inside,interpolated_pts_14],axis=0)
polygon_data_h14["AF"] = pd.concat([network_poly_inside_AF,network_poly_boundary_AF],axis=0)
print(f"The 95th percentile AF for h={h} is: {polygon_data_h14['AF'].quantile(q=0.95)}")
if print_figure: 
    # plot out the figure to show the network points
    fig, ax = plt.subplots(1,1)
    h14_AF_l1 = polygon_data_h14[['R14','X14']].where(polygon_data_h14['AF']<=1.0)
    ax.plot(h14_AF_l1['R14'], h14_AF_l1['X14'], marker='o', label='AF<=1', c='green', linestyle='none')
    h14_AF_btw1n2 = polygon_data_h14[['R14','X14']].where(
        polygon_data_h14['AF']>1.0).where(polygon_data_h14['AF']<2.0)
    ax.plot(h14_AF_btw1n2['R14'], h14_AF_btw1n2['X14'], marker='o', label='1<AF<=2', c='orange', linestyle='none')
    h14_AF_g2 = polygon_data_h14[['R14','X14']].where(polygon_data_h14['AF']>2.0)
    ax.plot(h14_AF_g2['R14'], h14_AF_g2['X14'], marker='o', label='AF>2', c='red', linestyle='none')
    ax.plot(ibr_h14['R14'].to_list() + [ibr_h14['R14'][0]], ibr_h14['X14'].to_list() + [ibr_h14['X14'][0]], 
            marker='o', label='Polygon Vertices', linestyle='-', color='blue')
    # labels and axis
    ax.set_xlabel('R (Ohms)')
    ax.set_ylabel('X (Ohms)')
    ax.set_title(f'Amplification factor plot for random points inside network polygon h={h}')
    ax.legend()
    fig.tight_layout()
    fig.savefig(f"polygon_AF_plot_h{h}.png")
    # plt.show()

########### PLOTTING THE RESULTS ##################
sensitivity_r = int(r_h)
sensitivity_x = int(x_h)

plot_soln_space(
    R_range, X_range, AF, h=h,
    site_r_h=r_h, site_x_h=x_h,
    plotter_r=sensitivity_r, plotter_x=sensitivity_x,
    polygon=ibr_project.polygon_data_dict[h],
    filename=filename+'_{:02d}'.format(h)
) if plot_figure else None