import pickle
import boto3
import os
import json

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
    
    # print("model: ", model)
    # return model

model = load_model()

def lambda_handler(event, context):
    try:
        # body = json.loads(event["body"])
        # features = body["features"]  # Expecting JSON: {"features": [values]}

        # prediction = model.predict([features]).tolist()

        return {
            "statusCode": 200,
            "body": json.dumps({"prediction": "test 2"})
        }

    except Exception as e:
        return {
            "statusCode": 500,
            "body": json.dumps({"error": str(e)})
        }