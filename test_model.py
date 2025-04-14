import pandas as pd
import pickle

def test_model():
    with open("../infra/bundles/model_1744656136812.pkl", "rb") as f:
        model = pickle.load(f)
    test_set = pd.read_csv("../infra/bundles/strat_test_set.csv")
    label_median_house_value = test_set['median_house_value'].copy()
    housing = test_set.drop("median_house_value", axis=1)

    for index, row in housing.head(10).iterrows():
        sample_house = pd.DataFrame(row.values.reshape(1, -1), columns=housing.columns.tolist())
        predicted_price = model.predict(sample_house)
        real_price = label_median_house_value.iloc[index]
        print(f"Row {index}: Predicted Price = {predicted_price[0]}, Real Price = {real_price}")
        
test_model()

    