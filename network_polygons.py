"""Script to focus on processing network polygon data that comes from NSPs.
Typically this comes in the form of a spreadsheet with harmonic ranges 2-50.

TODO: future improvements to this would establish the entire site
into an object class with different site specific data attached to it

Author: Inez Zheng (@zeniconcombres)
Date Created: 16/01/2024"""

import pandas as pd
import numpy as np
import random
from pandas import DataFrame as df
from matplotlib import pyplot as plt
from matplotlib.patches import Polygon
from shapely.geometry import Polygon, LineString, Point

# constants
H_ORDERS = 49 # number of harmonics in orders 2-50
H_ORDERS_RANGE = list(range(2,51))
R_HEADERS = [(f"R{str(i)}") for i in H_ORDERS_RANGE]
X_HEADERS = [(f"X{str(i)}") for i in H_ORDERS_RANGE]

class Project():
    def __init__(self, name=None) -> None:
        self.project_name = name
        self.h_R = df([])
        self.h_X = df([])
        self.polygon_data_dict = {}
        self.interpolated_polygon_points = {}
        self.points_inside_polygon = {}

    # def test_function():
    #     pass

    def input_network_data(self, input_filename, input_sheet='Sheet 1'):
        """Function reads data from an NSP spreadsheet with network polygon data in the
        following format and separates this out into individual R and X dataframes to be stored
        against harmonic order keys in the self.network_polygons dict.
        E.g. input data:
                 	    Harmonic #2	 	Harmonic #3	 	Harmonic #4	 	Harmonic #5	    ...
                R	    X	    R	    X	    R	    X	    R	    X       ...
        Point 1	8.78	28.99	31.38	44.89	31.9	17.34	9.1	    37.08   ...
        Point 2	11.54	24.95	36.27	34.36	35.57	9.03	18.51	12.7    ...
        Point 3	5.6	    15.03	24.1	28.35	14.94	1.32	7.98	39.77   ...
        Point 4	4.79	17.36	11.07	25.52	23.65	0.05	3.62	20.84   ...
        ...

        Args:
            input_filename (str): filename of the input spreadsheet
        """
        data = pd.read_excel(input_filename, sheet_name=input_sheet, index_col=0, header=1)
        print(data.head())
        data.reset_index(drop=True,inplace=True)
        assert len(data.columns)%H_ORDERS == 0, f"There are {len(data.columns)} columns!"
        
        # splitting out the DataFrame into resistance and inductance
        self.h_R = data.iloc[:,::2]
        self.h_R.columns = R_HEADERS
        self.h_X = data.iloc[:,1::2]
        self.h_X.columns = X_HEADERS

        # compiling this into the network polygon dictionary stored per harmonic order
        for h in H_ORDERS_RANGE:
            self.polygon_data_dict[h] = pd.concat(
                [self.h_R[f"R{str(h)}"], self.h_X[f"X{str(h)}"]], 
                axis=1
                )
        return self.polygon_data_dict

    def interpolate_polygon_points(self, h, num_pts=100, print_figure=False):
        """Function interpolates the network polygon corner points
        to create more points along the polygon boundary."""
        X = self.polygon_data_dict[h][f"X{h}"].to_list()
        R = self.polygon_data_dict[h][f"R{h}"].to_list()

        # Create a Polygon object from the vertices
        polygon = Polygon(zip(R, X))

        # Create a LineString object from the exterior of the polygon
        line = LineString(polygon.exterior)

        # Interpolate points along the edge of the polygon
        num_points = num_pts  # You can adjust the number of interpolated points
        interpolated_points = [line.interpolate(i / num_points, normalized=True) for i in range(num_points + 1)]

        # Extract x and y coordinates from the interpolated points
        interpolated_R = [point.x for point in interpolated_points]
        interpolated_X = [point.y for point in interpolated_points]

        interpolated_points = df([])
        interpolated_points[f"R{h}"] = interpolated_R
        interpolated_points[f"X{h}"] = interpolated_X
        self.interpolated_polygon_points[h] = interpolated_points

        if print_figure == True:
            # Plot the polygon and the interpolated points
            fig, ax = plt.subplots()
            ax.plot(R + [R[0]], X + [X[0]], marker='o', label='Polygon Vertices', linestyle='-', color='blue')
            ax.plot(interpolated_R, interpolated_X, marker='.', label='Interpolated Points', linestyle='-', color='red')
            ax.set_xlabel('R (Ohms)')
            ax.set_ylabel('X (Ohms)')
            ax.set_title(f'Interpolated impedance points along network polygon edges for h={h}')
            ax.legend()
            fig.savefig(f"{num_pts}polygon_points_interpolated_h{h}.png")
        return interpolated_points

    def generate_random_points_inside_polygon(self, h, num_points=1000, print_figure=False):
        """Function to generate random points inside the polygon"""
        X = self.polygon_data_dict[h][f"X{h}"].to_list()
        R = self.polygon_data_dict[h][f"R{h}"].to_list()

        # Create a Polygon object from the vertices
        polygon = Polygon(zip(R, X))

        points = []
        min_x, min_y, max_x, max_y = polygon.bounds

        # generate points
        while len(points) < num_points:
            random_point = Point(random.uniform(min_x, max_x), random.uniform(min_y, max_y))
            if random_point.within(polygon):
                points.append(random_point)

        # Extract x and y coordinates from the random points
        random_R = [point.x for point in points]
        random_X = [point.y for point in points]

        random_points_inside_poly = df([])
        random_points_inside_poly[f"R{h}"] = random_R
        random_points_inside_poly[f"X{h}"] = random_X
        self.points_inside_polygon[h] = random_points_inside_poly

        if print_figure == True: 
            # Plot the polygon, its vertices, and the random points
            fig, ax = plt.subplots()
            ax.plot(R + [R[0]], X + [X[0]], marker='o', label='Polygon Vertices', linestyle='-', color='blue')
            ax.plot(random_R, random_X, marker='.', label='Random Points', linestyle='None', color='green')
            ax.set_xlabel('R (Ohms)')
            ax.set_ylabel('X (Ohms)')
            ax.set_title(f'{num_points} random points inside network polygon h={h}')
            ax.legend()
            fig.savefig(f"{num_points}points_inside_polygon_h{h}.png")
        return random_points_inside_poly


    def plot_harmonic_polygon(self, h):
        # this one can probably replaced by something in plotter
        plot_data = self.polygon_data_dict[h]
        plot_data_for_line = plot_data.append(plot_data.iloc[0]).reset_index(drop=True)
        fig, ax = plt.subplots(1,1)
        x=plot_data[f"R{str(h)}"]
        y=plot_data[f"X{str(h)}"]
        ax.scatter(x, y, s=10, c='blue')
        ax.plot(plot_data_for_line.iloc[:,0], plot_data_for_line.iloc[:,1],linestyle='-', c='black')
        ax.set_title(f"Harmonic polygon for h={h}")
        ax.set_xlabel("R (Ohms)")
        ax.set_ylabel("X (Ohms)")
        return fig, ax