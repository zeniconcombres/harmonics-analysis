import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import os, sys, time
from matplotlib.colors import LinearSegmentedColormap

# CONSTANTS

# FUNCTIONS
def _gen_soln_space(xspan=[0,1000], yspan=[-1000,1000], step=1.0):
    # Define the ranges and steps for X and Y
    x_range = np.arange(xspan[0], xspan[1]+1, step)
    y_range = np.arange(yspan[0], yspan[1]+1, step)

    # Generate the meshgrid using np.meshgrid
    X, Y = np.meshgrid(x_range, y_range)
    return X, Y

def calc_amplification(x_h, r_h, v_bkg_h ,h=2, R_range=[0,1000], X_range=[-1000,1000], step=1.0):
    R, X = _gen_soln_space(xspan=R_range, yspan=X_range, step=step)

    # calculating the voltage split at each network impedance point
    v_drop_h = v_bkg_h * (r_h + 1j*x_h) / (r_h + 1j*x_h + R + X)
    amp_factor = abs(v_drop_h) / v_bkg_h
    print(f"The maximum amplification factor is {np.max(amp_factor)}.")

    # plotting the results
    plot_soln_space(
        R, X, amp_factor,
        x_h, r_h,
        savefig=True, filename="tester.png"
    )

    return amp_factor


def plot_soln_space(
        R, X, values,
        r_h, x_h,
        savefig=False, filename=None
    ):
    # Define a custom colormap from green to red
    colours = [(0, 'green'), 
               (1.5/np.max(values),'orange'), 
               (2/np.max(values),'red'), 
               (1, 'red')]
    cmap = LinearSegmentedColormap.from_list('custom_cmap', colours, N=256)

    # Create a 2D plot with color scale representing the magnitude of Z
    plt.imshow(
        np.abs(values), 
        extent=(np.min(R), np.max(R), np.min(X), np.max(X)), 
        cmap=cmap
    )

    # Add a colorbar to show the magnitude scale
    cbar = plt.colorbar(label='Magnitude')
    cbar.set_clim(0, np.max(values))

    # showing the site impedance on the plot
    plt.scatter(r_h, x_h, marker='x', s=200, color='black', linewidth=2, label="Site impedance")
    plt.legend(loc='lower center')

    # set labels and title
    plt.xlabel('R (ohms)')
    plt.ylabel('X (ohms)')
    plt.title('Plot of Amplification Factor')

    # set axes limits to show the axes at the origin
    plt.xlim(left=np.min(R), right=np.max(R))
    plt.ylim(bottom=np.min(X), top=np.max(X))

    # add grid lines
    plt.axhline(0, color='black', linewidth=0.5, linestyle='--')
    plt.axvline(0, color='black', linewidth=0.5, linestyle='--')

    # save the plot if desired
    plt.savefig(filename) if savefig else None
    return


if __name__ == "__main__":
    start_time = time.time()
    # if considering TG, 0.75% is half of 1.5% from the planning levels
    AF = calc_amplification(x_h=30.0, r_h=100.0, v_bkg_h=0.75,h=11) 
    # plot_soln_space(X,Y)
    runtime = round(time.time() - start_time, 1)
    print(f"Runtime: {runtime}s")
