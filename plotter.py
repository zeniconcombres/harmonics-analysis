"""Script that contains functions to plot harmonics data generated from 
the calculations in background_harmonics.py. Main script can call this. 

Author: Inez Zheng (@zeniconcombres)
Date Created: 16 Jan 2024"""

import plotly.graph_objects as go
from matplotlib.colors import LinearSegmentedColormap
from plotly.subplots import make_subplots
import matplotlib.pyplot as plt

def _gen_heatmap(R_range, X_range, ampfac):
    """Create a 2D heatmap with color scale representing the absolute value of Z"""
    heatmap = go.Heatmap(
        z=ampfac, x=R_range, y=X_range, 
        # colorscale=plotly_colorscale, name='Amplification Factor (AF)'
        colorscale='Viridis', name='Amplification Factor (AF)'
    )
    # Create contours to overlay the heatmap
    contours = go.Contour(
        z=ampfac, x=R_range, y=X_range,
        # colorscale=plotly_colorscale, name='AF contours'
        colorscale='Viridis', name='AF contours'
    )
    return heatmap, contours

def _gen_site_impedance(site_r_h, site_x_h):
    """Add a big white 'X' at point (30, 50)"""
    site_impedance = go.Scattergl(
        x=[site_r_h], y=[site_x_h], 
        mode='markers', 
        marker=dict(symbol='x', size=10, color='white'), 
        name=f'Site Impedance'
    )
    return site_impedance

def _gen_sensitivities(R_range, X_range, ampfac, r_h, x_h):
    """Line graph of amplification values for a given network point 
    to show the particular sensitivities around this point"""
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
    return line_graph_r, line_graph_x

def _gen_polygon_points(polygon,h):
    """Network polygon points to include"""
    poly_scatter = go.Scatter(
        x=polygon[f"R{str(h)}"],y=polygon[f"X{str(h)}"],
        mode='markers', 
        marker=dict(symbol='circle', size=5, color='orange'),
        name='Network polygon vertices'
    )
    polygon_for_line = polygon
    polygon_for_line.loc[len(polygon)] = polygon.iloc[0]
    poly_line = go.Scatter(
        x=polygon_for_line[f"R{str(h)}"],y=polygon_for_line[f"X{str(h)}"],
        mode='lines', name='Network polygon'
    )
    return poly_scatter, poly_line

def plot_soln_space(
        R_range, X_range, ampfac, site_r_h, site_x_h,
        plotter_r=0.0, plotter_x=100.0, h=2, polygon=None,
        filename=None
    ):
    """This function plots out the amplification factor results. The plot generates
    an html output which has interactive toggles. The graphs can also be
    exported as .png or other image formats based on a given filename. 

    Args:
        R_range (numpy.ndarray): evenly spaced numbers across a range of R
            to form the X axis of the surface plot
        X_range (numpy.ndarray): evenly spaced numbers across a range of X
            to form the Y axis of the surface plot
        ampfac (list): meshgrid of the amplification factors over the R and X surface.
        site_r_h (float, optional): site aggregate resistance in Ohms (R)
        site_x_h (float, optional): site aggregate inductance / capacitance in Ohms (X)
        plotter_r (float, optional): impedance point's resistance value
            to appear in the focus plots to show sensitivity. Defaults to 0.0.
        plotter_x (float, optional): impedance point's resistance value 
            to appear in the focus plots to show sensitivity. Defaults to 100.0.
        # TODO: takee seensitivity point as a float not just integer
        h (int, optional): harmonic order the graphs represent. Defaults to 2.
        filename (str, optional): for example, '2023-10-10_plots.png'. Defaults to None.
    """
    # Define a custom colormap from green to red
    # TODO: originally wanted to create a customised colour scale but the front end
    # is a bit fiddly to adjust the scales in the colourmap hence deleting for now

    # generate plot objects for each subplot
    heatmap, contours = _gen_heatmap(R_range, X_range, ampfac)
    site_impedance = _gen_site_impedance(site_r_h, site_x_h)
    # print(ampfac) TODO!!!
    try:
        line_graph_r, line_graph_x = _gen_sensitivities(R_range, X_range, ampfac, r_h=plotter_r, x_h=plotter_x)
    except:
        print("Given sensitivity point failed to find a trace in the AF dataframe. Trying a default R=0.0 and X = 100.0.")
        line_graph_r, line_graph_x = _gen_sensitivities(R_range, X_range, ampfac, r_h=0.0, x_h=100.0)

    # Create the layout
    layout = go.Layout(
        title=f'Plot of Amplification Factor for h={h}', 
        showlegend=False
    )

    # Create subplots with one row and two columns
    fig = make_subplots(
        rows=1, cols=3, subplot_titles=[
        'Amplification change over X', 
        'Amplification change over R', 
        'Amplification Factor'
        ], column_widths=[0.2, 0.35, 0.45]
    )

    # Add line graph to the left subplot
    fig.add_trace(line_graph_x, row=1, col=1)
    fig.update_xaxes(title_text='X (Ohms)', row=1, col=1)
    fig.update_yaxes(title_text='Amplification Factor', row=1, col=1)

    # Add line graph to the right subplot
    fig.add_trace(line_graph_r, row=1, col=2)
    fig.update_xaxes(title_text='R (Ohms)', row=1, col=2)
    fig.update_yaxes(title_text='Amplification Factor', row=1, col=2)

    # Add heatmap plot to the right hand side subplot
    fig.add_trace(heatmap, row=1, col=3)
    fig.add_trace(contours, row=1, col=3)
    fig.update_xaxes(title_text='R (Ohms)', row=1, col=3)
    fig.update_yaxes(title_text='X (Ohms)', row=1, col=3)

    # Add 'X' marker to show the site impedance to the same subplot
    fig.add_trace(site_impedance, row=1, col=3)

    # If polygon information is provided, add this to the heatmap plot
    if not(polygon.empty):
        poly_scatter, poly_line = _gen_polygon_points(polygon,h)
        fig.add_trace(poly_scatter, row=1, col=3)
        fig.add_trace(poly_line, row=1, col=3)

   # Update the layout to use different horizontal domains for the main subplot and the inner subplot
    fig.update_layout(
        xaxis=dict(domain=[0, 0.2]),  # Inner subplot
        xaxis2=dict(domain=[0.3, 0.5]),  # Inner subplot
        xaxis3=dict(domain=[0.6, 1.0]),  # Main subplot
    )

    # Update the layout
    fig.update_layout(layout)

    # Save the interactive plot to a HTML file
    fig.write_html("interactive_"+filename+".html") if filename else None

    plt.close()
    return

def plot_network_polygon(plot_data, h):
    """Function that plots the network polygons when taking in a dataframe for the polygon
    corner points. Example input:
         R2      X2
    1    6.005   4.0135
    2    3.023   3.1548
    ...
    10   103.12  7.2391

    Can also be used in conjunction with the site object for plot_data input. 
    e.g. ibr_project.polygon_data_dict[h]
    
    Args:
        plot_data (DataFrame): polygon corner points
        h (integer): harmonic order

    Returns:
        fig, ax: figure and axis from pyplot
    """
    plot_data_for_line = plot_data
    plot_data_for_line.loc[len(plot_data),:] = plot_data.iloc[0,:]
    plot_data_for_line.reset_index(drop=True, inplace=True)
    assert len(plot_data_for_line) > len(plot_data), f"There might be something wrong with the polygon. The input data has {len(plot_data)} points."
    fig, ax = plt.subplots(1,1)
    x=plot_data[f"R{str(h)}"]
    y=plot_data[f"X{str(h)}"]
    ax.scatter(x, y, s=10, c='blue')
    ax.plot(plot_data_for_line.iloc[:,0], plot_data_for_line.iloc[:,1],linestyle='-', c='black')
    ax.set_title(f"Harmonic polygon for h={h}")
    ax.set_xlabel("R (Ohms)")
    ax.set_ylabel("X (Ohms)")
    return fig, ax
