from pathlib import Path
import pandas as pd
import tarfile
import urllib.request
import numpy as np
from build_model.preprocessing_pipeline import PreprocessingPipeline
from build_model.train_and_evaluate import TrainAndEvaluate
from build_model.fine_tune_model import FineTuneModel
from build_model.evaluate_model import EvaluateModel
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import FunctionTransformer
from sklearn.metrics.pairwise import rbf_kernel
from sklearn.ensemble import RandomForestRegressor
import pprint
# # import joblib
import pickle
import time

def generate_model():
    def load_housing_data():
        tarball_path = Path("../datasets/housing.tgz")

        if not tarball_path.is_file():
            Path("../datasets").mkdir(parents=True, exist_ok=True)
            url = "https://github.com/ageron/data/raw/main/housing.tgz"
            urllib.request.urlretrieve(url, tarball_path)
            with tarfile.open(tarball_path) as housing_tarball:
                housing_tarball.extractall(path="datasets")
        return pd.read_csv(Path("../datasets/housing/housing.csv"))

    def get_test_train_sets(housing):
        #################################################################################################################################
        # median income is important for calculating median housing price
        # you should not have too many strata, and each stratum should be large enough.
        # create an income category attribute with five categories
        housing["income_cat"] = pd.cut(housing["median_income"],
                                    bins=[0., 1.5, 3.0, 4.5, 6., np.inf],
                                    labels=[1, 2, 3, 4, 5])

        housing["income_cat"].value_counts().sort_index().plot.bar(rot=0, grid=True)
        # random sampling (we not gonna use in in the end)
        # train_set, test_set = train_test_split(housing, test_size=0.2, random_state=42)

        # Stratified sampling based on the income category
        strat_train_set, strat_test_set = train_test_split(
            housing, test_size=0.2, stratify=housing["income_cat"], random_state=42)

        # important to use stat data sets, not rundom
        # init_val = housing["income_cat"].value_counts() / len(housing)
        # non_start_val = test_set["income_cat"].value_counts() / len(test_set)
        # start_val = strat_test_set["income_cat"].value_counts() / len(strat_test_set)

        # print('======>start_val val:', start_val)
        # print('======>non_start_val val:', non_start_val)
        # print('======>init_val val:', init_val)
        # strat split is much closer to original data ratio

        # We won’t use the income_cat column again, so we can as well drop it, reverting the data back to its original state:
        for set_ in (strat_train_set, strat_test_set):
            set_.drop("income_cat", axis=1, inplace=True)

        return strat_train_set, strat_test_set

    def add_useful_attributes(housing):
        housing["rooms_per_house"] = housing["total_rooms"] / housing["households"]
        housing["bedrooms_ratio"] = housing["total_bedrooms"] / housing["total_rooms"]
        housing["people_per_house"] = housing["population"] / housing["households"]
        return housing

    def revert_to_clean_training_set(housing):
        housing = strat_train_set.drop("median_house_value", axis=1)
        label_median_house_value = strat_train_set["median_house_value"].copy()
        return housing, label_median_house_value

    # measure the geographic similarity between each district and San Francisco:
    def measure_geo_similarity(housing):
        sf_coords = 37.7749, -122.41
        sf_transformer = FunctionTransformer(rbf_kernel, kw_args=dict(Y=[sf_coords], gamma=0.1))
        simil = sf_transformer.transform(housing[["latitude", "longitude"]])
        print('======>simil:', simil)

    # 1. load data
    init_housing = load_housing_data()
    # 2. getting training and test sets
    strat_train_set, strat_test_set = get_test_train_sets(init_housing)
    strat_test_set.to_csv('../infra/bundles/strat_test_set.csv', index=False)
    # we explore only strat_train_set
    # from now our housing is a copy of strat_train_set
    housing = strat_train_set.copy()

    # 3. getting prepared/preprocessed housing data
    housing = add_useful_attributes(housing)
    housing, label_median_house_value = revert_to_clean_training_set(housing)
    preprocessing_pipeline = PreprocessingPipeline(housing)
    preprocessor = preprocessing_pipeline.get_preprocessor()

    # 4. training and finding best performing models
    train_and_evaluate = TrainAndEvaluate(housing, preprocessor, label_median_house_value)

    # print('linear regression model')
    # lin_regression_model = train_and_evaluate.train_linear_regression()
    # train_and_evaluate.get_model_rmses(lin_regression_model)

    # print('decision tree model')
    # decision_tree_model = train_and_evaluate.train_decision_tree()
    # train_and_evaluate.get_model_rmses(decision_tree_model)

    #SLOW but best performing model
    print('random forest model')
    random_forest_model = train_and_evaluate.train_random_forest()
    train_and_evaluate.get_model_rmses(random_forest_model)

    #Fast hgb model
    # print('hgb model')
    # hgb_model = train_and_evaluate.train_hgb()
    # train_and_evaluate.get_model_rmses(hgb_model)

    # 5. Fine-Tune Model
    print('tuning started')
    fine_tune_model = FineTuneModel(housing, preprocessor, label_median_house_value)
    rnd_best_params_, rnd_cv_results_, rnd_cv_results_df, final_model = fine_tune_model.find_best_hyper_params(
        RandomForestRegressor, search_method='random'
    )
    feature_importances = final_model['random_forest'].feature_importances_
    # Sorting importance scores in descending order and display them next to their corresponding attribute names:
    res = sorted(zip(feature_importances, final_model["preprocessing"].get_feature_names_out()), reverse=True)
    pprint.pprint(res)

    # Evaluate final model on the Test Set
    evaluate_model = EvaluateModel(strat_test_set, final_model)
    final_rmse, comparison = evaluate_model.get_final_results()
    print('======>final_rmse:', final_rmse) #41448.084299370465
    print('======>comparison:', comparison) #[39293.29060201 43496.26073402]

    # Saving model, using pickle library
    current_time_ms = int(time.time() * 1000)
    Path("../infra/bundles").mkdir(parents=True, exist_ok=True)
    model_filename = f"model_{current_time_ms}.pkl"
    with open(f"../infra/bundles/{model_filename}", "wb") as f:
        pickle.dump(final_model, f)
    print(f"Model saved as {model_filename}")

generate_model()