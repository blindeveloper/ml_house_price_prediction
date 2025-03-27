import matplotlib.pyplot as plt
from pandas.plotting import scatter_matrix
import numpy as np

class DataVisualizer:
    def __init__(self, data):
        self.data = data

    def show_data_info(self):
        print('======>self.data.info():', self.data.info())
        print('======>self.data.head():', self.data.head())
        print('======>self.data.describe():', self.data.describe())

    def show_geographical_data(self):
        # Because the dataset includes geographical information (latitude and longitude), 
        # it is a good idea to create a scatterplot of all the districts to visualize the data 
        self.data.plot(kind="scatter", x="longitude", y="latitude", grid=True, alpha=0.1)

        # The radius of each circle represents the district’s population (option s), and the color represents the price
        self.data.plot(kind="scatter", x="longitude", y="latitude", grid=True,
                    s=self.housing["population"] / 100, label="population",
                    c="median_house_value", cmap="jet", colorbar=True,
                    legend=True, sharex=False, figsize=(10, 7))

        # This image tells you that the housing prices are very much related to the location (e.g., close to the ocean) and to the population density. 
        # A clustering algorithm should be useful for detecting the main cluster 
        # and for adding new features that measure the proximity to the cluster centers. 
        # The ocean proximity attribute may be useful as well, 
        # although in Northern California the housing prices in coastal districts are not too high, so it is not a simple rule.
        plt.show()

    def show_corelation_matrix(self, attr):
        # BECAUSE OF ERROR "could not convert string to float: 'NEAR BAY'", WE NEED TO CONVERT THE CATEGORICAL ATTRIBUTE ocean_proximity TO NUMERICAL VALUES"
        # Since the dataset is not too large, you can easily compute the standard correlation coefficient
        housing_num = self.data.select_dtypes(include=[np.number])
        corr_matrix = housing_num.corr()
        print('==================================>corr_matrix:', corr_matrix)
        # cor = corr_matrix[attr].sort_values(ascending=False)
        # print('======>cor:', cor)

    def show_scatter_matrix_corelation(self):
        attributes = ["median_house_value", "median_income", "total_rooms",
                    "housing_median_age"]
        scatter_matrix(self.housing[attributes], figsize=(12, 8))
        plt.show()

    def show_median_income_corelation(self): 
        self.data.plot(kind="scatter", x="median_income", y="median_house_value",
                alpha=0.1, grid=True)
        plt.show()
