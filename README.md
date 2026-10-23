# Global Dams Explorer

A Streamlit app for exploring the relationship between **dam height** and **reported reservoir capacity** across dam purposes.

## Features
- Height–capacity scatterplot with a logarithmic capacity axis
- Interactive dam-purpose filter
- Observation count and Spearman correlation
- Filters for country and purpose
- Textual explanations

## Data
Source: [Global Dam Watch (GDAT v1)](https://www.globaldamwatch.org/database).

Download the dams CSV and upload it through the app's sidebar. Select the filters to investigate data.

## Run locally
```bash
python -m pip install -r requirements.txt
python -m streamlit run global_dams_app.py
```

## Analysis and limitations
The Jupyter notebook contains data cleaning and EDA. Reservoir capacity is missing for **55.48%** of dams; analyses use available positive measurements, so comparisons may be biased. Correlation does not imply causation.

**Next step:** Expand analysis of geographic and historical patterns.

