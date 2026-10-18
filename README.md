# Global Dams Explorer

A small Streamlit dashboard for exploring how **dam height** relates to **reported reservoir capacity**, and how this relationship differs by a dam's main purpose. The project is intended for students, researchers, and people interested in water infrastructure.

## Current features

- Scatterplot of dam height (meters) versus reported reservoir capacity (million m³)
- Logarithmic Y-axis to make widely varying reservoir capacities easier to compare
- Interactive filter for one or more dam purposes
- Observation count and Spearman correlation calculated for the selected dams

## Dataset

**Source:** [Global Dam Watch — Database](https://www.globaldamwatch.org/database) (GDAT v1 dams dataset).

Download the GDAT v1 **dams CSV** from the data source. The dataset is **not included in this repository**. Either:

1. Upload the CSV in the application's left sidebar when prompted; or
2. Place it next to `global_dams_app.py`, named `GDAT_v1_dams.csv` (the export filename `GDAT_v1_dams.xlsx - GDAT_v1_dams.csv` is also supported).

The app uses `Main_P_Map` (purpose), `Height` (m), and `Volume_Rep` (million m³). Purpose spellings are standardized, and numeric fields are converted for analysis. For this particular GDAT v1 CSV export, capacity is stored in decimal-comma format with 15 digits after the comma; the conversion in the app is specific to this data format.

## Run locally

Install Python (preferably Python 3.10 or later). In a terminal opened inside the project folder:

```bash
python -m pip install -r requirements.txt
python -m streamlit run global_dams_app.py
```

Streamlit will display a local URL (usually `http://localhost:8501`). Open the page, provide the CSV if requested, and select dam purposes to explore.

## Analysis notebook

The Jupyter notebook contains the data-quality checks and exploratory data analysis (EDA1 boxplots and EDA2 correlation/scatterplot). **Add your completed `.ipynb` notebook to this repository** alongside the app, or in a `notebooks/` folder.

## Interpretation and limitations

- The chart includes only dams with valid, positive height and capacity measurements; missing capacity values are not imputed.
- Missing values are common, especially for reservoir capacity. The analysis sample has a different mix of dam purposes from the full dataset, so its results may not represent all dams equally.
- The logarithmic Y-axis changes the display, not the original capacity data.
- Correlations describe associations, not causes. Extreme values may need separate verification.

## AI-use disclosure

ChatGPT was used for assistance with code development, troubleshooting Streamlit dependencies and data conversion, and drafting explanations/documentation. Numerical results were checked against the project dataset and Jupyter analyses. The project author reviewed the output and is responsible for the final submitted work.
