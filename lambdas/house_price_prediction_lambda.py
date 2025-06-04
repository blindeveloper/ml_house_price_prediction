import pickle
import boto3
import os
import json
import numpy as np
import sklearn
import pandas as pd
from build_model.preprocessing_pipeline import PreprocessingPipeline

s3 = boto3.client("s3")

# Load Model from S3
def load_model():
    bucket = os.getenv("MODEL_S3_BUCKET")
    key = os.getenv("MODEL_S3_KEY")
    local_path = "/tmp/model_v3.pkl"

    print('bucket: ', bucket)
    print('key: ', key)

    # Download the file to /tmp
    s3.download_file(bucket, key, local_path)
    
    # Load the model from the local file
    with open(local_path, "rb") as f:
        model = pickle.load(f)

    return model

model = load_model()

def lambda_handler(event, context):
    try:
        body = json.loads(event["body"])

        data = {
            "longitude": body["longitude"],
            "latitude": body["latitude"],
            "housing_median_age": body["housing_median_age"],
            "total_rooms": body["total_rooms"],
            "total_bedrooms": body["total_bedrooms"],
            "population": body["population"],
            "households": body["households"],
            "median_income": body["median_income"],
            "ocean_proximity": body["ocean_proximity"]
        }
        h_columnns = ['longitude', 'latitude', 'housing_median_age', 'total_rooms', 'total_bedrooms', 'population', 'households', 'median_income', 'ocean_proximity']
        df = pd.DataFrame(data)
        for index, row in df.iterrows():
            sample_house = pd.DataFrame(row.values.reshape(1, -1), columns=h_columnns)
            predicted_price = model.predict(sample_house)[0]
            # real_price = 397700.0
        return {
            "statusCode": 200,
            "body": json.dumps({"predicted_price": predicted_price })
        }

    except Exception as e:
        return {
            "statusCode": 500,
            "body": json.dumps({"error": str(e)})
        }