"""Script to focus on processing network polygon data that comes from NSPs.
Typically this comes in the form of a spreadsheet with harmonic ranges 2-50.

TODO: future improvements to this would establish the entire site
into an object class with different site specific data attached to it

Author: Inez Zheng (@zeniconcombres)
Date Created: 16/01/2024"""

import pandas as pd
import numpy as np
from pandas import DataFrame as df
from matplotlib import pyplot as plt
from matplotlib.patches import Polygon

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