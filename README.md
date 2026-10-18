# Global Dams Explorer

A Streamlit app for exploring the relationship between **dam height** and **reported reservoir capacity** across dam purposes.

## Features
- Height–capacity scatterplot with a logarithmic capacity axis
- Interactive dam-purpose filter
- Observation count and Spearman correlation

## Data
Source: [Global Dam Watch (GDAT v1)](https://www.globaldamwatch.org/database).

Download the dams CSV and upload it through the app's sidebar, or save it as `GDAT_v1_dams.csv` beside `global_dams_app.py`. The app handles the decimal-comma format of capacity values in this export.

## Run locally
```bash
python -m pip install -r requirements.txt
python -m streamlit run global_dams_app.py
```

## Analysis and limitations
The Jupyter notebook contains data cleaning and EDA. Reservoir capacity is missing for **55.48%** of dams; analyses use available positive measurements, so comparisons may be biased. Correlation does not imply causation.

**Next step:** Add a country filter.
