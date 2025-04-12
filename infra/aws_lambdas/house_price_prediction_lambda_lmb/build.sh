# Get the current timestamp in milliseconds to create a unique filename
current_time_ms=$(date +%s%3N)
file_name="house_price_prediction_lmb_${current_time_ms}.zip"
# Create a zip file containing the installed Python packages
zip -r9 ${file_name} lambda_function.py

# Move the zip file to the bundles folder two levels up
mv ${file_name} ../../bundles/