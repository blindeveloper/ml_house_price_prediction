#!/bin/bash
# Set the directory where Python packages will be installed
export PKG_DIR="python"
mkdir -p ${PKG_DIR}
# Get the current timestamp in milliseconds to create a unique filename
current_time_ms=$(date +%s%3N)
file_name="scikit_learn_layer_${current_time_ms}.zip"

# Use a Docker container with the lambci/lambda image to install Python dependencies
docker run --rm -v $(pwd):/foo -w /foo lambci/lambda:build-python3.8 \
    pip install -r scikit_learn_requirements.txt --no-deps -t ${PKG_DIR}

# Create a zip file containing the installed Python packages
zip -r9 ${file_name} ./python/

# Move the zip file to the bundles folder two levels up
mv ${file_name} ../infra/bundles/

# Clean up the `${PKG_DIR}` directory and recreate it as an empty directory
rm -rf ${PKG_DIR}
echo "${file_name} generated"