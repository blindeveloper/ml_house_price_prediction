from sklearn.metrics import root_mean_squared_error
import numpy as np
from scipy import stats


class EvaluateModel:
    def __init__(self, strat_test_set, final_model):
        self.strat_test_set = strat_test_set
        self.final_model = final_model
        self.confidence = 0.95

    def get_final_results(self):
        # Get the predictors and the labels from your test set, X_test and y_test
        X_test = self.strat_test_set.drop("median_house_value", axis=1)
        y_test = self.strat_test_set["median_house_value"].copy()
        # run your final_model to transform the data and make predictions
        final_predictions = self.final_model.predict(X_test)
        # evaluate these predictions
        rmse_error = root_mean_squared_error(y_test, final_predictions)
        # to have an idea of how precise this estimate is,
        # compute a 95% confidence interval for the generalization error
        squared_errors = (final_predictions - y_test) ** 2
        comparison = np.sqrt(
            stats.t.interval(self.confidence, len(squared_errors) - 1, 
            loc=squared_errors.mean(), 
            scale=stats.sem(squared_errors))
        )
        return rmse_error, comparison
        