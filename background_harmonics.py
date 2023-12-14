"""The script contains functions that calculate the background amplification factor
for a given harmonic order based on given impedance of a site (x_h, r_h) across an area of 
network impedances (X, R). 

Created by: Inez Zheng (@zeniconcombres)
Created on: 11/12/23
"""

import pandas as pd
import numpy as np
import plotly.graph_objects as go
# import matplotlib.pyplot as plt
import time
from matplotlib.colors import LinearSegmentedColormap

# CONSTANTS

# FUNCTIONS
def gen_soln_space(xspan=[0,1000], yspan=[-1000,1000], step=1.0):
    # Define the ranges and steps for X and Y
    x_range = np.arange(xspan[0], xspan[1]+1, step)
    y_range = np.arange(yspan[0], yspan[1]+1, step)

    # Generate the meshgrid using np.meshgrid
    X, Y = np.meshgrid(x_range, y_range)
    return X, Y, x_range, y_range

def calc_amplification(x_h, r_h, v_bkg_h, R, X, h=2):
    # calculating the voltage split at each network impedance point
    v_drop_h = v_bkg_h * (r_h + 1j*x_h) / (r_h + 1j*x_h + R + X)
    amp_factor = abs(v_drop_h) / v_bkg_h
    print(f'The maximum amplification factor for h={h} is {np.max(amp_factor)}.')
    return amp_factor

def plot_soln_space(
        R_range, X_range, values,
        r_h, x_h, h,
        filename=None
    ):
    # Define a custom colormap from green to red
    colours = [(0, 'green'), 
               (1.5/np.max(values),'orange'), 
               (2/np.max(values),'red'), 
               (1, 'red')]
    cmap = LinearSegmentedColormap.from_list('custom_cmap', colours, N=256)

    # Convert the Matplotlib colormap to a Plotly colorscale
    cmap_colors = [cmap(i) for i in range(cmap.N)]
    plotly_colorscale = [
        [
            float(i) / (len(cmap_colors)-1), 
            f'rgb{tuple(int(255 * c) for c in cmap_colors[i][:3])}'
        ] for i in range(len(cmap_colors))
    ]

    # Create a 2D heatmap with color scale representing the absolute value of Z
    heatmap = go.Heatmap(
        z=values, x=R_range, y=X_range, 
        colorscale=plotly_colorscale, name='Amplification Factor'
    )

    # Add a big white 'X' at point (30, 50)
    scatter = go.Scattergl(
        x=[r_h], y=[x_h], 
        mode='markers', 
        marker=dict(symbol='x', size=10, color='white'), 
        name='Impedance'
    )

    # Create the layout
    layout = go.Layout(
        title=f'Plot of Amplification Factor for h={h}',
        xaxis=dict(title='R (ohms)'),
        yaxis=dict(title='X (ohms)'),
        # showlegend=True,
        coloraxis=dict(
            cmin=0,
            cmax=np.max(values),
            colorbar=dict(title='Amplification Factor')  # Set the color bar title
        )
    )

    # Create the figure
    fig = go.Figure(data=[heatmap, scatter], layout=layout)

    # Save the interactive plot to a HTML file
    fig.write_html("interactive_"+filename+".html")
    return


if __name__ == "__main__":
    start_time = time.time()
    # Network impedance range to be scanned across
    x_range = [-1000,1000]
    r_range = [0,1000]
    step = 1.0
    R, X, R_range, X_range = gen_soln_space(xspan=r_range, yspan=x_range, step=step)
    # if considering TG, 0.75% is half of 1.5% from the planning levels
    AF = calc_amplification(x_h=30.0, r_h=100.0, v_bkg_h=0.75, R=R, X=X, h=11) 
    # plot_soln_space(X,Y)
    runtime = round(time.time() - start_time, 1)
    print(f"Runtime: {runtime}s")
