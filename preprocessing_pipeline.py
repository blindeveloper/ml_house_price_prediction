
from sklearn.pipeline import make_pipeline
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import OneHotEncoder, StandardScaler, FunctionTransformer
from claster_similarity import ClusterSimilarity
from sklearn.compose import ColumnTransformer
from sklearn.compose import make_column_selector
import numpy as np
from sklearn.pipeline import make_pipeline
from sklearn.compose import make_column_selector


# def apply_replace_missing_values(housing):
#     imputer = SimpleImputer(strategy="median")
#     # imputer can work only with numbers
#     # print('======>housing.head():', housing.head())
#     # housing_num = housing.select_dtypes(include=[np.number])
#     imputer.fit(housing)
#     # imputer computed the median of EACH attribute and stored the result in its statistics_ instance variable.
#     # print('======>imputer.statistics_:', imputer.statistics_)
#     X = imputer.transform(housing)
#     return pd.DataFrame(X, columns=housing.columns,
#                           index=housing.index)

# def apply_replace_text_cat_with_numerical(housing, category):
#     cat_encoder = OneHotEncoder()
#     # convert the categorical attribute ocean_proximity to numerical values
#     housing_cat = housing[[category]]
#     cat_encoder.fit_transform(housing_cat)
#     housing_cat_1hot = cat_encoder.transform(housing_cat).toarray()
#     housing_cat_df = pd.DataFrame(housing_cat_1hot, 
#                                   columns=[f"{category}_{cat}" for cat in cat_encoder.categories_[0]],
#                                   index=housing.index)
#     housing = pd.concat([housing, housing_cat_df], axis=1)
#     housing.drop('ocean_proximity', axis=1, inplace=True)
#     return housing

# def apply_scale_min_max(housing):
#     min_max_scaler = MinMaxScaler(feature_range=(-1, 1))
#     # Select columns that do NOT contain 'ocean_proximity' in their names
#     columns_to_scale = [col for col in housing.columns if 'ocean_proximity' not in col]
#     # Apply MinMaxScaler only to selected columns
#     housing[columns_to_scale] = min_max_scaler.fit_transform(housing[columns_to_scale])
#     return housing

# def apply_scale_standartization(housing):
#     std_scaler = StandardScaler()
#     columns_to_scale = [col for col in housing.columns if 'ocean_proximity' not in col]
#     housing[columns_to_scale] = std_scaler.fit_transform(housing[columns_to_scale])
#     return housing

# def transformed_target_regressor(housing, new_data):
#     model = TransformedTargetRegressor(LinearRegression(), transformer=StandardScaler())
#     model.fit(housing[["median_income"]], housing_labels)
#     predictions = model.predict(new_data)
#     return predictions

# def apply_transform_log(housing, category):
#     transform_log = FunctionTransformer(np.log, inverse_func=np.exp)
#     housing[category] = transform_log.transform(housing[[category]])
#     return housing

# def apply_transform_gaussian_rbf_similarity_measure(housing, category):
#     rbf_transformer = FunctionTransformer(rbf_kernel, kw_args=dict(Y=[[35.]], gamma=0.1))
#     housing[category] = rbf_transformer.transform(housing[["housing_median_age"]])
#     return housing



# housing_num_no_nun_min_max_scaled = (housing
#            .pipe(apply_replace_text_cat_with_numerical, 'ocean_proximity')
#            .pipe(apply_replace_missing_values)
#            .pipe(apply_transform_log, 'population')
#         #    .pipe(apply_transform_gaussian_rbf_similarity_measure, 'population')
#            .pipe(apply_scale_min_max)
#         #    .pipe(apply_scale_standartization)
#            )

# target_scaler = StandardScaler()
# scaled_labels = target_scaler.fit_transform(housing_labels.to_frame())

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

    def column_ratio(self, X):
        return X[:, [0]] / X[:, [1]]

    def ratio_name(self, function_transformer, feature_names_in):
        return ["ratio"]  # feature names out

    def ratio_pipeline(self):
        return make_pipeline(
            SimpleImputer(strategy="median"),
            FunctionTransformer(self.column_ratio, feature_names_out=self.ratio_name),
            StandardScaler())

    def get_preprocessing(self):
        cluster_simil = ClusterSimilarity(n_clusters=10, gamma=1., random_state=42)

        num_pipeline = make_pipeline(SimpleImputer(strategy="median"), StandardScaler())
        cat_pipeline = make_pipeline(SimpleImputer(strategy="most_frequent"), OneHotEncoder(handle_unknown="ignore"))
        log_pipeline = make_pipeline(
            SimpleImputer(strategy="median"), 
            FunctionTransformer(np.log, feature_names_out="one-to-one"), 
            StandardScaler()
        )

        return ColumnTransformer([
                ("bedrooms", self.ratio_pipeline(), ["total_bedrooms", "total_rooms"]),
                ("rooms_per_house", self.ratio_pipeline(), ["total_rooms", "households"]),
                ("people_per_house", self.ratio_pipeline(), ["population", "households"]),
                ("log", log_pipeline, ["total_bedrooms", "total_rooms", "population",
                                    "households", "median_income"]),
                ("geo", cluster_simil, ["latitude", "longitude"]),
                ("cat", cat_pipeline, make_column_selector(dtype_include=object)),
            ],
            remainder=num_pipeline)  # one column remaining: housing_median_age
