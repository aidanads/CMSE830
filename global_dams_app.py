"""Global Dams Explorer: interactive, descriptive analysis of GDAT v1."""
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
import streamlit as st

st.set_page_config(page_title="Global Dams Explorer", layout="wide")

PURPOSE_FIXES = {
    "Water supply": "Water Supply",
    "Flood control": "Flood Control",
    "Other/Not Specified": "Other",
}
DATA_FILENAMES = (
    "GDAT_v1_dams.csv",
    "GDAT_v1_dams.xlsx - GDAT_v1_dams.csv",
)

# High-contrast neon colors.
PURPOSE_COLORS = {
    "Hydroelectricity": "#00E5FF",  # cyan
    "Flood Control": "#FFB020",     # amber
    "Irrigation": "#B388FF",        # violet
    "Water Supply": "#39FFA5",     # green
    "Recreation": "#FF55C3",       # pink
    "Livestock": "#F7FA58",        # lime
    "Navigation": "#FF6F61",       # coral
    "Fisheries": "#55A7FF",        # blue
    "Other": "#E1E6EE",            # light neutral for unspecified purpose
}
PLOT_BG = "#090F1C"
AXIS_BG = "#111A2B"
PLOT_TEXT = "#F2F6FC"
TICK_TEXT = "#D1D9E5"
GRID_COLOR = "#46556D"


def style_dark_plot(fig, ax):
    """a dark background."""
    fig.patch.set_facecolor(PLOT_BG)
    ax.set_facecolor(AXIS_BG)
    ax.set_axisbelow(True)
    ax.grid(axis="y", color=GRID_COLOR, linewidth=0.65, alpha=0.55)
    ax.tick_params(axis="both", colors=TICK_TEXT)
    ax.title.set_color(PLOT_TEXT)
    ax.xaxis.label.set_color(PLOT_TEXT)
    ax.yaxis.label.set_color(PLOT_TEXT)
    for spine in ax.spines.values():
        spine.set_color(GRID_COLOR)
    legend = ax.get_legend()
    if legend is not None:
        legend.get_frame().set_facecolor(AXIS_BG)
        legend.get_frame().set_edgecolor(GRID_COLOR)
        legend.get_title().set_color(PLOT_TEXT)
        for item in legend.get_texts():
            item.set_color(TICK_TEXT)


def unavailable_purposes(selected_names, available_data, selected_data):
    available = set(available_data["Main_P_Map"].dropna())
    counts = selected_data["Main_P_Map"].value_counts()
    return [
        f"{purpose} ({int(counts.get(purpose, 0))} matching records)"
        for purpose in selected_names
        if purpose not in available
    ]


@st.cache_data(show_spinner="Loading dam data...")
def load_and_clean(source):
    raw = pd.read_csv(source, low_memory=False)
    needed = ["Admin0", "Main_P_Map", "Height", "Volume_Rep"]
    missing = [column for column in needed if column not in raw.columns]
    if missing:
        raise ValueError(f"Missing columns in CSV: {', '.join(missing)}")

    data = raw[needed].copy()
    data["Main_P_Map"] = data["Main_P_Map"].replace(PURPOSE_FIXES)
    data["Height"] = pd.to_numeric(data["Height"], errors="coerce")

    # This particular GDAT v1 CSV has 15 decimal places after a decimal comma.
    # Example: '15,400000000000000' means 15.4 million m³.
    # The conversion below is specific to this export format.
    data["Volume_Rep"] = (
        pd.to_numeric(
            data["Volume_Rep"].astype("string").str.replace(",", "", regex=False),
            errors="coerce",
        ) / 10**15
    ).astype("float64")
    return data


st.title("Global Dams Explorer")
st.write(
    "**Question:** How do dam heights and reported reservoir capacities differ "
    "by main purpose and country?"
)
st.caption(
    "Source: Global Dam Watch (GDAT v1). Each record represents a dam. "
    "Intended audience: students, researchers, and water-infrastructure planners."
)

with st.sidebar:
    st.header("Filters")
    uploaded = st.file_uploader("Upload GDAT v1 dams CSV", type="csv")

local_csv = next(
    (p for name in DATA_FILENAMES if (p := Path(__file__).with_name(name)).exists()),
    None,
)
source = uploaded if uploaded is not None else local_csv
if source is None:
    st.info("Upload the GDAT v1 dams CSV in the sidebar to begin.")
    st.stop()

try:
    df = load_and_clean(source)
except (ValueError, pd.errors.ParserError, UnicodeDecodeError) as error:
    st.error(f"Could not read the CSV: {error}")
    st.stop()

countries = sorted(df["Admin0"].dropna().unique().tolist())
purposes = sorted(df["Main_P_Map"].dropna().unique().tolist())

with st.sidebar:
    selected_country = st.selectbox("Country", ["All countries"] + countries)
    selected_purposes = st.multiselect(
        "Dam purpose", purposes, default=purposes,
        help="Both visualizations and their statistics update when you change these filters.",
    )

if not selected_purposes:
    st.warning("Select at least one dam purpose.")
    st.stop()

selected = df[df["Main_P_Map"].isin(selected_purposes)].copy()
if selected_country != "All countries":
    selected = selected[selected["Admin0"] == selected_country]
if selected.empty:
    st.warning("No records match the current filters.")
    st.stop()

# EDA1 needs observed height only; EDA2 needs both measurements.
height_df = selected[selected["Height"] > 0].copy()
capacity_df = selected[
    (selected["Height"] > 0) & (selected["Volume_Rep"] > 0)
].copy()

col1, col2, col3 = st.columns(3)
col1.metric("Dam records selected", f"{len(selected):,}")
col2.metric("With height (EDA1)", f"{len(height_df):,}")
col3.metric("With height and capacity (EDA2)", f"{len(capacity_df):,}")

height_tab, capacity_tab = st.tabs([
    "EDA1 — Height by purpose", "EDA2 — Height vs. capacity"
])

with height_tab:
    st.subheader("How do dam heights differ across purposes?")
    missing_height_purposes = unavailable_purposes(
        selected_purposes, height_df, selected
    )
    if missing_height_purposes:
        st.warning(
            "Not displayed in EDA1: " + ", ".join(missing_height_purposes)
            + ". There are no matching records with positive measured height "
            "for these purposes. This does not mean such dams do not exist."
        )
    if height_df.empty:
        st.info("No positive height measurements are available for this selection.")
    else:
        height_summary = (
            height_df.groupby("Main_P_Map")["Height"]
            .agg(
                Count="count", Median="median",
                Q1=lambda x: x.quantile(0.25),
                Q3=lambda x: x.quantile(0.75),
            )
            .sort_values("Median", ascending=False)
        )
        height_summary["IQR"] = height_summary["Q3"] - height_summary["Q1"]

        fig, ax = plt.subplots(figsize=(10, 5))
        sns.boxplot(
            data=height_df, x="Main_P_Map", y="Height", hue="Main_P_Map",
            order=height_summary.index, hue_order=height_summary.index,
            palette=PURPOSE_COLORS, dodge=False,
            boxprops={"edgecolor": "#E9F1FF", "linewidth": 1.25},
            whiskerprops={"color": "#E9F1FF", "linewidth": 1.2},
            capprops={"color": "#E9F1FF", "linewidth": 1.2},
            medianprops={"color": "#FFFFFF", "linewidth": 2.1},
            showfliers=False, ax=ax,
        )
        if ax.get_legend() is not None:
            ax.get_legend().remove()
        ax.set_title("Dam Height by Main Purpose")
        ax.set_xlabel("Main Purpose")
        ax.set_ylabel("Dam Height (m)")
        ax.tick_params(axis="x", rotation=30)
        style_dark_plot(fig, ax)
        fig.tight_layout()
        st.pyplot(fig)
        plt.close(fig)

        if len(height_summary) > 1:
            highest = height_summary.index[0]
            lowest = height_summary.index[-1]
            st.write(
                f"**In this selection:** {highest} has the highest median height "
                f"({height_summary.loc[highest, 'Median']:.1f} m); "
                f"{lowest} has the lowest "
                f"({height_summary.loc[lowest, 'Median']:.1f} m)."
            )
        st.caption(
            "Boxes show the middle 50% of measured heights; outlier markers are "
            "hidden for readability, not removed from the data."
        )
        with st.expander("View height statistics by purpose"):
            st.dataframe(height_summary.round(2), use_container_width=True)

with capacity_tab:
    st.subheader("Are taller dams associated with larger reservoirs?")
    missing_capacity_purposes = unavailable_purposes(
        selected_purposes, capacity_df, selected
    )
    if missing_capacity_purposes:
        st.warning(
            "Not displayed in EDA2: " + ", ".join(missing_capacity_purposes)
            + ". These selected purposes have no matching records with BOTH "
            "positive dam height and reported reservoir capacity under the current "
            "filters. This does not mean such dams do not exist."
        )
    if len(capacity_df) < 2:
        st.info("At least two dams with positive height and capacity are required.")
    else:
        rho = capacity_df["Height"].corr(
            capacity_df["Volume_Rep"], method="spearman"
        )
        st.metric(
            "Spearman correlation for this selection",
            f"{rho:.3f}" if pd.notna(rho) else "N/A",
        )
        st.caption(
            "Spearman correlation measures a rank-based association, not causation."
        )

        available_purposes = [
            purpose for purpose in selected_purposes
            if purpose in capacity_df["Main_P_Map"].unique()
        ]

        fig, ax = plt.subplots(figsize=(10, 5))
        sns.scatterplot(
            data=capacity_df, x="Height", y="Volume_Rep", hue="Main_P_Map",
            hue_order=available_purposes, palette=PURPOSE_COLORS,
            alpha=0.6 if len(capacity_df) > 1500 else 0.86,
            s=17 if len(capacity_df) > 1500 else 28,
            linewidth=0, ax=ax,
        )
        ax.set_yscale("log")
        ax.set_title("Dam Height vs. Reported Reservoir Capacity")
        ax.set_xlabel("Dam Height (m)")
        ax.set_ylabel("Reported Reservoir Capacity (million m³, log scale)")
        ax.legend(title="Main Purpose", loc="upper left", bbox_to_anchor=(1.02, 1))
        style_dark_plot(fig, ax)
        fig.tight_layout()
        st.pyplot(fig)
        plt.close(fig)

        if pd.notna(rho):
            strength = (
                "very weak" if abs(rho) < 0.2 else
                "weak" if abs(rho) < 0.4 else
                "moderate" if abs(rho) < 0.6 else "strong"
            )
            direction = "positive" if rho > 0 else "negative" if rho < 0 else "zero"
            place = selected_country if selected_country != "All countries" else "all countries"
            st.write(
                f"**What this means:** Among **{len(capacity_df):,} dams** "
                f"with usable height and capacity measurements in **{place}**, "
                f"Spearman correlation is **{rho:.3f}**, a **{strength} {direction}** "
                "rank-based association. Higher dams tend to be associated with "
                "larger reservoirs when the correlation is positive, but there is "
                "substantial variation between individual dams."
                if rho > 0 else
                f"**What this means:** Among **{len(capacity_df):,} dams** in "
                f"**{place}**, Spearman correlation is **{rho:.3f}**, a "
                f"**{strength} {direction}** rank-based association."
            )
            st.caption(
                "This is ONE correlation for all displayed purposes combined; "
                "it is not the correlation for each purpose separately. "
                "Use 'Compare correlations by dam purpose' below to see groups. "
                "These terms describe association strength, not causation."
            )
            if len(capacity_df) < 30:
                st.info("Interpret carefully: fewer than 30 usable dams are shown.")

        with st.expander("Compare correlations by dam purpose"):
            rows = []
            for purpose, group in capacity_df.groupby("Main_P_Map"):
                rows.append({
                    "Main purpose": purpose,
                    "Count": len(group),
                    "Spearman": group["Height"].corr(group["Volume_Rep"], method="spearman"),
                })
            corr_summary = pd.DataFrame(rows).set_index("Main purpose")
            st.dataframe(
                corr_summary.sort_values("Count", ascending=False).round(3),
                use_container_width=True,
            )
        st.caption(
            "Capacity uses a logarithmic display scale because values are strongly "
            "right-skewed; the underlying values are unchanged."
        )

missing_rate = selected["Volume_Rep"].isna().mean() * 100
st.divider()
st.markdown("**Important data limitation**")
st.write(
    f"Reported reservoir capacity is missing for {missing_rate:.1f}% of the "
    f"{len(selected):,} selected records. Missingness varies by purpose and country, "
    "so observations with available values may not represent all dams equally. "
    "No missing measurements were imputed; unusually large values may need verification."
)
