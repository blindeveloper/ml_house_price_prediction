from sklearn.pipeline import Pipeline
from sklearn.model_selection import GridSearchCV

class FineTuneModel:
    def __init__(self, housing, preprocessing, housing_labels):
        self.housing = housing
        self.preprocessing = preprocessing
        self.housing_labels = housing_labels

    def get_model_best_params(self, regressor_function):
        full_pipeline = Pipeline([
            ("preprocessing", self.preprocessing),
            ("random_forest", regressor_function(random_state=42)),
        ])
        param_grid = [
            {'preprocessing__geo__n_clusters': [5, 8, 10],
            'random_forest__max_features': [4, 6, 8]},
            {'preprocessing__geo__n_clusters': [10, 15],
            'random_forest__max_features': [6, 8, 10]},
        ]

        grid_search = GridSearchCV(full_pipeline, param_grid, cv=3, scoring='neg_root_mean_squared_error')
        grid_search.fit(self.housing, self.housing_labels)
        return grid_search.best_params_, grid_search.cv_results_