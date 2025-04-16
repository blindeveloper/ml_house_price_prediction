import pandas as pd
import pickle

def test_model():
    with open("../infra/bundles/model_1744656136812.pkl", "rb") as f:
        model = pickle.load(f)
    test_set = pd.read_csv("../infra/bundles/strat_test_set.csv")

    # print('======>test_set:', test_set)

    label_median_house_value = test_set['median_house_value'].copy()
    housing = test_set.drop("median_house_value", axis=1)
    housing_columns = housing.columns.tolist()

    print('======>housing_columns:', housing_columns)

    data = {
        "longitude": [-121.95],
        "latitude": [37.11],
        "housing_median_age": [21.0],
        "total_rooms": [2387.0],
        "total_bedrooms": [357.0],
        "population": [913.0],
        "households": [341.0],
        "median_income": [7.736],
        # "median_house_value": [397700.0],
        "ocean_proximity": ["<1H OCEAN"]
    }
    df = pd.DataFrame(data)

    for index, row in df.iterrows():
        sample_house = pd.DataFrame(row.values.reshape(1, -1), columns=housing_columns)
        # print('======>sample_house:', sample_house)
        predicted_price = model.predict(sample_house)
        real_price = label_median_house_value.iloc[index]
        print(f"Row {index}: Predicted Price = {predicted_price[0]}, Real Price = 397700.0")
        
test_model()

    