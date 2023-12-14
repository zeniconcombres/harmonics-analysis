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
from pandas import DataFrame as df
from matplotlib.colors import LinearSegmentedColormap
from plotly.subplots import make_subplots

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
        R_range, X_range, ampfac,
        r_h, x_h, h,
        filename=None
    ):
    # Define a custom colormap from green to red
    colours = [(0, 'green'), 
               (1.5/np.max(ampfac),'orange'), 
               (2/np.max(ampfac),'red'), 
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
        z=ampfac, x=R_range, y=X_range, 
        colorscale=plotly_colorscale, name='Amplification Factor'
    )

    # Add a big white 'X' at point (30, 50)
    scatter = go.Scattergl(
        x=[r_h], y=[x_h], 
        mode='markers', 
        marker=dict(symbol='x', size=10, color='white'), 
        name='Impedance'
    )

    # Line graph of amplification values for the given site inductance r_h and x_h
    ampfac_df = df(ampfac, index=X_range, columns=R_range)
    print(ampfac_df.head())
    # print(ampfac_df.loc[:,[r_h]])
    # grabbing the r_h and x_h data into separate dataframes
    # r_h_df =  ampfac_df.loc[:,[r_h]]

    line_graph_x = go.Scatter(
        x=X_range,
        y=ampfac[:,[i[0] for i in enumerate(R_range) if i[1]==r_h]].transpose()[0],
        mode='lines', name='Amplification change over X'
        )

    line_graph_r = go.Scatter(
        x=R_range,
        y=ampfac[[i[0] for i in enumerate(X_range) if i[1]==x_h]][0],
        mode='lines', name='Amplification change over R'
        )

    # Create the layout
    layout = go.Layout(
        title=f'Plot of Amplification Factor for h={h}', 
        showlegend=False
    )

    # Create subplots with one row and two columns
    fig = make_subplots(rows=1, cols=3, subplot_titles=[
        'Amplification change over X',
        'Amplification change over R',
        'Amplification Factor'
        ], column_widths=[0.2, 0.2, 0.6])

    # Add line graph to the upper left subplot
    fig.add_trace(line_graph_x, row=1, col=1)
    fig.update_xaxes(title_text='X (Ohms)', row=1, col=1)
    fig.update_yaxes(title_text='Amplification Factor', row=1, col=1)

    # Add line graph to the bottom left subplot
    fig.add_trace(line_graph_r, row=1, col=2)
    fig.update_xaxes(title_text='R (Ohms)', row=1, col=2)
    fig.update_yaxes(title_text='Amplification Factor', row=1, col=2)

    # Add heatmap plot to the right hand side subplot
    fig.add_trace(heatmap, row=1, col=3)
    fig.update_xaxes(title_text='R (Ohms)', row=1, col=3)
    fig.update_yaxes(title_text='X (Ohms)', row=1, col=3)
        # showlegend=True,
        # coloraxis=dict(
        #     cmin=0,
        #     cmax=np.max(ampfac),
        #     colorbar=dict(title='Amplification Factor')  # Set the color bar title
        # )

    # Add 'X' marker to show the site impedance to the same subplot
    fig.add_trace(scatter, row=1, col=3)

    # Update the layout
    fig.update_layout(layout)

    # Create the figure
    # fig = go.Figure(data=[heatmap, scatter], layout=layout)

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
