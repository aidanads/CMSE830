""" Global Dams Explorer prototype using GDAT v1."""
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
import streamlit as st

st.set_page_config(page_title="Global Dams Explorer", layout="wide")
st.title("Global Dams Explorer")
st.write(
    "Explore how dam height relates to reported reservoir capacity "
    "and compare patterns across main dam purposes."
)

# The original GDAT CSV can be uploaded in the app.
data_files = [
    Path(__file__).with_name("GDAT_v1_dams.csv"),
    Path(__file__).with_name("GDAT_v1_dams.xlsx - GDAT_v1_dams.csv"),
]
data_path = next((p for p in data_files if p.exists()), None)
if data_path is not None:
    source = data_path
else:
    source = st.file_uploader("Upload the GDAT v1 dams CSV", type="csv")
    if source is None:
        st.info("Upload the GDAT v1 CSV to start exploring, or place it next to the app file.")
        st.stop()

raw = pd.read_csv(source, low_memory=False)
df = raw[["Main_P_Map", "Height", "Volume_Rep"]].copy()
df["Main_P_Map"] = df["Main_P_Map"].replace({
    "Water supply": "Water Supply",
    "Flood control": "Flood Control",
    "Other/Not Specified": "Other",
})
df["Height"] = pd.to_numeric(df["Height"], errors="coerce")
# In this GDAT v1 CSV, Volume_Rep is stored as decimal-comma text
# with 15 decimal places (e.g., "15,400000000000000").
# Remove the comma and restore its position by dividing by 10**15.
df["Volume_Rep"] = (
    pd.to_numeric(
        df["Volume_Rep"].astype("string").str.replace(",", "", regex=False),
        errors="coerce",
    ) / 10**15
)

# Including observations suitable for the log-scale scatterplot.
plot_df = df.dropna(subset=["Height", "Volume_Rep", "Main_P_Map"])
plot_df = plot_df[(plot_df["Height"] > 0) & (plot_df["Volume_Rep"] > 0)]

purposes = sorted(plot_df["Main_P_Map"].unique())
default_purposes = [
    p for p in ["Hydroelectricity", "Irrigation", "Water Supply"] if p in purposes
]
selected_purposes = st.multiselect(
    "Compare dam purposes", purposes, default=default_purposes
)
if not selected_purposes:
    st.warning("Select at least one dam purpose to display results.")
    st.stop()

selected_df = plot_df[plot_df["Main_P_Map"].isin(selected_purposes)]
correlation = selected_df["Height"].corr(
    selected_df["Volume_Rep"], method="spearman"
)
st.write(f"**Dams shown:** {len(selected_df):,}")
st.write(f"**Spearman correlation:** {correlation:.3f}")

# Dark2; neutral gray for the 'Other' category.
colors = dict(zip(
    [p for p in purposes if p != "Other"], sns.color_palette("Dark2", 8)
))
colors["Other"] = "#777777"

fig, ax = plt.subplots(figsize=(10, 5))
sns.scatterplot(
    data=selected_df, x="Height", y="Volume_Rep", hue="Main_P_Map",
    hue_order=selected_purposes, palette=colors, alpha=0.35, s=18, ax=ax
)
ax.set_yscale("log")
ax.set_title("Dam Height vs. Reservoir Capacity by Purpose")
ax.set_xlabel("Dam Height (m)")
ax.set_ylabel("Reported Reservoir Capacity (million m³, log scale)")
ax.legend(title="Main Purpose", loc="upper left", bbox_to_anchor=(1.02, 1))
fig.tight_layout()
st.pyplot(fig)
plt.close(fig)

st.caption(
    "Only dams with reported positive height and reservoir capacity are shown. "
    "Missing capacity values are not imputed; results may not represent all dams."
)
