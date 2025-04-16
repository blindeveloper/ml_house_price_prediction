#!/bin/bash
# Set the directory where Python packages will be installed
export PKG_DIR="python"
mkdir -p ${PKG_DIR}
# Get the current timestamp in milliseconds to create a unique filename
current_time_ms=$(date +%s%3N)
file_name="external_pkgs_layer_${current_time_ms}.zip"

# Use a Docker container with the lambci/lambda image to install Python dependencies
docker run --rm --platform linux/arm64 -v $(pwd):/foo -w /foo public.ecr.aws/sam/build-python3.9:latest \
    pip install -r external_pkgs_requirements.txt --no-deps --no-cache-dir -t ${PKG_DIR}

# Remove unnecessary files to reduce the zip size
find ${PKG_DIR} -name "*.dist-info" -type d -exec rm -rf {} +
find ${PKG_DIR} -name "*.egg-info" -type d -exec rm -rf {} +
find ${PKG_DIR} -name "__pycache__" -type d -exec rm -rf {} +
find ${PKG_DIR} -name "tests" -type d -exec rm -rf {} +
find ${PKG_DIR} -name "docs" -type d -exec rm -rf {} +

# Create a zip file containing the installed Python packages
zip -r9 ${file_name} ./python/

# Move the zip file to the bundles folder two levels up
mv ${file_name} ../infra/bundles/

# Clean up the `${PKG_DIR}` directory and recreate it as an empty directory
rm -rf ${PKG_DIR}
echo "${file_name} generated"