# Description:
This is house price prediction project running based on Linear regression algorithm.
Goal is to Achieve around 90% accuracy on the test dataset.

# Installation process:
**Init new virtual environment**
`python3 -m venv venv`

**Activate the virtual environment**
`source venv/bin/activate`

**Install Libraries from requirements.txt**
`pip3 install -r requirements.txt`

**Run**
`python3 main.py`

# INFRA
# Generating AWS layers
1. Go to: `cd scripts`
2. Run: `./build_external_packages_layer.sh`
3. zip file of layer will be placed in **infra/bundles** folder as output of this command

# Generating AWS Lambdas
1. Go to: `cd scripts`
2. Run: `./build_house_price_prediction_lmb.sh`
3. zip file of lambda will be placed in **infra/bundles** folder as output of this command 