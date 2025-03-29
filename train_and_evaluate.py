from sklearn.pipeline import make_pipeline
from sklearn.linear_model import LinearRegression
from sklearn.tree import DecisionTreeRegressor
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import cross_val_score
import pandas as pd
from sklearn.ensemble import HistGradientBoostingRegressor



# Train and Evaluate on the Training Set
# lin_reg = make_pipeline(preprocessing, LinearRegression())
# lin_reg.fit(housing, housing_labels)
# # You now have a working linear regression model. 
# # You try it out on the training set, looking at the first five predictions and comparing them to the labels
# housing_predictions = lin_reg.predict(housing)
# set_1 = housing_predictions[:5].round(-2)  # -2 = rounded to the nearest hundred
# # array([243700., 372400., 128800.,  94400., 328300.])
# set_2 = housing_labels.iloc[:5].values
# # array([458300., 483800., 101700.,  96100., 361800.])
# print('======>set_1:', set_1)
# print('======>set_2:', set_2)
# # the first prediction is way off (by over $200,000)

# You chose to use the RMSE(Root Mean Squared Error) as your performance measure, 
# so you want to measure this regression model’s RMSE on the whole training set using root_mean_squared_error function, 
# lin_rmse = root_mean_squared_error(housing_labels, housing_predictions)
# print('======>lin_rmse:', lin_rmse) #68972.88910758459

# The median_housing_values of most districts range between $120,000 and $265,000, 
# so a typical prediction error of $68,628 is really not very satisfying.
# This is an example of a model UNDERFITTING the training data.
# When this happens it can mean that the features do not provide enough information to make good predictions, 
# or that the model is not powerful enough.

# FIX: 
# to select a more powerful model, 
# to feed the training algorithm with better features, 
# or to reduce the constraints on the model.

# trying a DecisionTreeRegressor model
# tree_reg = make_pipeline(preprocessing, DecisionTreeRegressor(random_state=42))
# tree_reg.fit(housing, housing_labels)

# Now that the model is trained, you evaluate it on the training set:
# housing_predictions = tree_reg.predict(housing)
# tree_rmse = root_mean_squared_error(housing_labels, housing_predictions)
# print('======>tree_rmse:', tree_rmse) #0.0, overfitting

# Evaluation Using Cross-Validation
class TrainAndEvaluate:
    def __init__(self, housing, preprocessing, housing_labels):
        self.housing = housing
        self.preprocessing = preprocessing
        self.housing_labels = housing_labels

    # LinearRegression model
    def train_linear_regression(self):
        lin_reg = make_pipeline(self.preprocessing, LinearRegression())
        lin_reg.fit(self.housing, self.housing_labels)
        return lin_reg

    # DecisionTreeRegressor model
    def train_decision_tree(self):
        tree_reg = make_pipeline(self.preprocessing, DecisionTreeRegressor(random_state=42))
        tree_reg.fit(self.housing, self.housing_labels)
        return tree_reg
    
    # DecisionTreeRegressor model
    def train_hgb(self):
        hgb_reg = make_pipeline(self.preprocessing, HistGradientBoostingRegressor(random_state=42))
        hgb_reg.fit(self.housing, self.housing_labels)
        return hgb_reg

    # RandomForestRegressor model
    # ===========Providev best results but it takes a lot of time to calculate================
    def train_random_forest(self):
        # Set n_jobs=-1 to use all available CPU cores.
        forest_reg = make_pipeline(self.preprocessing, RandomForestRegressor(random_state=42, n_jobs=-1))
        forest_reg.fit(self.housing, self.housing_labels)
        return forest_reg

    def get_model_rmses(self, model):
        # Scikit-learn’s cross_val_score returns negative RMSE values when using neg_root_mean_squared_error as the scoring metric.
        # The reason: Scikit-learn’s convention is that higher scores are better, but RMSE is an error metric (lower is better). 
        # So, it negates RMSE to make it consistent with other scoring metrics.
        rmses = -cross_val_score(model, self.housing, self.housing_labels, scoring="neg_root_mean_squared_error", cv=10) 
        print('======>', pd.Series(rmses).describe())