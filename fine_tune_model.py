from sklearn.pipeline import Pipeline
from sklearn.model_selection import GridSearchCV
import pandas as pd
from scipy.stats import randint
from sklearn.model_selection import RandomizedSearchCV

class FineTuneModel:
    def __init__(self, housing, preprocessing, housing_labels):
        self.housing = housing
        self.preprocessing = preprocessing
        self.housing_labels = housing_labels

    def find_best_hyper_params(self, regressor_function, search_method='grid'):
        full_pipeline = Pipeline([
            ("preprocessing", self.preprocessing),
            ("random_forest", regressor_function(random_state=42)),
        ])

        if search_method == 'grid':
            params = [
                {'preprocessing__geo__n_clusters': [5, 8, 10],
                'random_forest__max_features': [4, 6, 8]},
                {'preprocessing__geo__n_clusters': [10, 15],
                'random_forest__max_features': [6, 8, 10]},
            ]
            search = GridSearchCV(full_pipeline, params, cv=3, scoring='neg_root_mean_squared_error')
        elif search_method == 'random':
            params = {
                'preprocessing__geo__n_clusters': randint(low=3, high=50),
                'random_forest__max_features': randint(low=2, high=20)
            }
            search = RandomizedSearchCV(
                full_pipeline, 
                param_distributions=params, 
                n_iter=10, 
                cv=3, 
                scoring='neg_root_mean_squared_error', 
                random_state=42,
                n_jobs=-1
            )

        search.fit(self.housing, self.housing_labels)
        # getting list of all the test scores for each combination of hyperparameters and for each cross-validation split, 
        # as well as the mean test score across all splits:
        cv_res = pd.DataFrame(search.cv_results_)
        cv_res.sort_values(by="mean_test_score", ascending=False, inplace=True)
        # show rmse = -score
        columns_to_convert = ["split0_test_score", "split1_test_score", "split2_test_score", "mean_test_score"]
        cv_res[columns_to_convert] = cv_res[columns_to_convert].abs()
        cv_results_df = cv_res[[
            "param_preprocessing__geo__n_clusters",
            "param_random_forest__max_features", 
            "split0_test_score",
            "split1_test_score",
            "split2_test_score",
            "mean_test_score",
        ]].head()

        return search.best_params_, search.cv_results_, cv_results_df, search.best_estimator_