
from sklearn.pipeline import make_pipeline
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import OneHotEncoder, StandardScaler, FunctionTransformer
from sklearn.compose import ColumnTransformer
from sklearn.compose import make_column_selector
from build_model.claster_similarity import ClusterSimilarity
import numpy as np
from sklearn.pipeline import make_pipeline
import pandas as pd

# This class automates feature engineering by applying ratios, log transformations, clustering, and scaling.
# 	Why is this useful?
# 	Ratios like bedrooms per room provide useful insights.
# 	Log transformations reduce skewness in numerical distributions.
# 	ClusterSimilarity helps incorporate location-based patterns.


# This code creates a ClusterSimilarity transformer, setting the number of clusters to 10. 
# Then it calls fit_transform() with the latitude and longitude of every district in the training set, 
# weighting each district by its median house value. 
# The transformer uses k-means to locate the clusters, 
# then measures the Gaussian RBF similarity between each district and all 10 cluster centers. 
# The result is a matrix with one row per district, and one column per cluster.
# cluster_simil = ClusterSimilarity(n_clusters=10, gamma=1., random_state=42)
# similarities = cluster_simil.fit_transform(housing_num_no_nun_min_max_scaled[["latitude", "longitude"]], sample_weight=housing_labels)
# # print('======>:', similarities[:3].round(2))



# PIPLINE FOR PREPROCESSING DATA
# Missing values in numerical features will be imputed by replacing them with the median, as most ML algorithms don’t expect missing values. 
# In categorical features, missing values will be replaced by the most frequent category. 
# The categorical feature will be one-hot encoded, as most ML algorithms only accept numerical inputs. 
# A few ratio features will be computed and added: bedrooms_ratio, rooms_per_house, and people_per_house. Hopefully these will better correlate with the median house value, and thereby help the ML models.
# A few cluster similarity features will also be added. These will likely be more useful to the model than latitude and longitude. 
# Features with a long tail will be replaced by their logarithm, as most models prefer features with roughly uniform or Gaussian distributions. 
# All numerical features will be standardized, as most ML algorithms prefer when all features have roughly the same scale.

class PreprocessingPipeline:
    def __init__(self, housing):
        self.housing = housing

    #This function calculates the ratio of two numerical columns.
    #X is expected to be a 2D NumPy array where the first column (X[:, [0]]) is divided by the second (X[:, [1]]).
    # Example:
    # If X = [[10, 2], [30, 6]], the output will be: [[5], [5]]
    # This transformation is useful for creating derived features like bedroom-to-room ratio.
    def column_ratio(self, X):
        return X[:, [0]] / X[:, [1]]

    # This method ensures that the transformed feature is named "ratio" in the final dataset.
    def ratio_name(self, function_transformer, feature_names_in):
        return ["ratio"]  # feature names out

    def ratio_pipeline(self):
        return make_pipeline(
            # Fills missing values with the median.
            SimpleImputer(strategy="median"),
            # Computes the column ratio.
            FunctionTransformer(self.column_ratio, feature_names_out=self.ratio_name),
            # Standardizes the ratio by scaling it to have mean 0 and variance 1.
            StandardScaler())
    
    def get_X_transformed(self, preprocessor):
        feature_names = preprocessor.get_feature_names_out()
        # Convert transformed NumPy array to DataFrame
        X_transformed = preprocessor.fit_transform(self.housing)
        X_transformed_df = pd.DataFrame(X_transformed, columns=feature_names)
        return X_transformed, X_transformed_df

    def get_preprocessor(self):
        # Uses ClusterSimilarity to generate cluster-based features from latitude and longitude.
        cluster_simil = ClusterSimilarity(n_clusters=10, gamma=1., random_state=42)

        # Handles numerical columns by imputing missing values and scaling them.
        num_pipeline = make_pipeline(
            SimpleImputer(strategy="median"), 
            StandardScaler()
        )

        # Handles categorical columns by imputing missing values and applying one-hot encoding.
        cat_pipeline = make_pipeline(
            SimpleImputer(strategy="most_frequent"), 
            OneHotEncoder(handle_unknown="ignore")
        )

        # Applies a log transformation to certain numerical columns, then scales them.
        log_pipeline = make_pipeline(
            SimpleImputer(strategy="median"), 
            FunctionTransformer(np.log, feature_names_out="one-to-one"), 
            StandardScaler()
        )

        # Uses ColumnTransformer to apply different pipelines to different feature sets
        return ColumnTransformer([
                ("bedrooms", self.ratio_pipeline(), ["total_bedrooms", "total_rooms"]),
                ("rooms_per_house", self.ratio_pipeline(), ["total_rooms", "households"]),
                ("people_per_house", self.ratio_pipeline(), ["population", "households"]),

                # Log Transformation: Applied to ["total_bedrooms", "total_rooms", "population", "households", "median_income"]
                ("log", log_pipeline, ["total_bedrooms", "total_rooms", "population", "households", "median_income"]),

                # Geographical Clustering: Uses latitude and longitude to assign cluster similarity.
                ("geo", cluster_simil, ["latitude", "longitude"]),
                
                # Categorical Encoding: Encodes categorical features using one-hot encoding.
                ("cat", cat_pipeline, make_column_selector(dtype_include=object)),
        ], remainder=num_pipeline)  # one column remaining: housing_median_age
