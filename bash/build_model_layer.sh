
#!/bin/bash
# Get the current timestamp in milliseconds to create a unique filename
current_time_ms=$(date +%s%3N)
file_name="build_model_layer_${current_time_ms}.zip"

mkdir -p layer/python
cp -r ../build_model layer/python/

cd layer
zip -r9 ${file_name} ./python/
mv ${file_name} ../../infra/bundles/

cd ..
rm -rf layer