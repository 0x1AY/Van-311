# Van 311 Analytics

## Overview

The Van 311 Analytics project aims to analyze the 311 service data for Vancouver to uncover patterns, identify service bottlenecks, and recommend solutions to enhance the efficiency and quality of the 311 system. The project leverages datasets on service requests, inquiry volumes, and contact center metrics to provide a data-driven foundation for actionable improvements.

# Project Structure

- .devcontainer/
- devcontainer.json
- .gitignore
- app.py
- data/
- 3-1-1-contact-centre-metrics.csv
- 3-1-1-inquiry-volume.csv
- 3-1-1-service-requests-2009-2021.csv
- 3-1-1-service-requests.csv
- 311service-requests.csv
- Closure_Reason_Categorization.csv
- service_requests_final.csv
- Vancouver_Neighborhood_Geocodes.csv
- main.ipynb
- README.md
- requirements.txt
- service_requests_dropna.csv
- service_requests.csv

# Installation

`````git clone https://github.com/0x1AY/Van-311.git
cd Van-311
## Install the required dependencies:
``` pip install -r requirements.txt ```
# Usage
## Running the Streamlit App

To run the Streamlit app, execute the following command:
````streamlit run app.py

`````
