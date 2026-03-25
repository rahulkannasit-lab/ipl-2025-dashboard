import pandas as pd
import streamlit as st
import plotly.express as px

# ================================
# LOAD DATA
# ================================
DATA_FILE = "ipl2025_over_summary.csv"
df = pd.read_csv(DATA_FILE)

st.set_page_config(page_title="IPL 2025 Over-wise Dashboard", layout="wide")
st.title("🏏 IPL 2025 Over-wise Dashboard")

# ================================
# CLEAN DATA
# ================================
df["batting_order"] = df["innings"].apply(
    lambda x: "First Batting" if x == 1 else "Second Batting"
)

df["over"] = pd.to_numeric(df["over"], errors="coerce")
df = df.dropna(subset=["over"]).copy()
df["over"] = df["over"].astype(int)

# Fix 0-19 → 1-20
if df["over"].min() == 0 and df["over"].max() <= 19:
    df["over"] = df["over"] + 1

# ================================
# SIDEBAR FILTERS
# ================================
st.sidebar.header("Filters")

teams = sorted(df["batting_team"].dropna().unique())
venues = sorted(df["venue"].dropna().unique())
matches = sorted(df["match_no"].dropna().unique())
overs = sorted(df["over"].dropna().unique())

selected_team = st.sidebar.selectbox("Batting Team", ["All"] + teams)
selected_opposition = st.sidebar.selectbox("Opposition (Bowling Team)", ["All"] + teams)
selected_venue = st.sidebar.selectbox("Venue", ["All"] + venues)
selected_match = st.sidebar.selectbox("Match", ["All"] + list(matches))
selected_over = st.sidebar.selectbox("Over", ["All"] + list(overs))
selected_batting_order = st.sidebar.selectbox(
    "Batting Order",
    ["All", "First Batting", "Second Batting"]
)

# ================================
# FILTER FUNCTION
# ================================
def apply_filters(df):
    temp = df.copy()

    if selected_team != "All":
        temp = temp[temp["batting_team"] == selected_team]

    if selected_opposition != "All":
        temp = temp[temp["bowling_team"] == selected_opposition]

    if selected_venue != "All":
        temp = temp[temp["venue"] == selected_venue]

    if selected_match != "All":
        temp = temp[temp["match_no"] == selected_match]

    if selected_batting_order != "All":
        temp = temp[temp["batting_order"] == selected_batting_order]

    return temp

filtered = apply_filters(df).sort_values(["match_no", "innings", "over"])

# ================================
# KPI SUMMARY
# ================================
st.subheader("Summary")

k1, k2, k3, k4, k5 = st.columns(5)
k1.metric("Matches Found", filtered["match_no"].nunique())
k2.metric("Runs", int(filtered["runs_in_over"].sum()))
k3.metric("Wickets", int(filtered["wickets_in_over"].sum()))
k4.metric("4s", int(filtered["fours"].sum()))
k5.metric("6s", int(filtered["sixes"].sum()))

# ================================
# SINGLE MATCH VIEW
# ================================
if filtered["match_no"].nunique() == 1:

    st.subheader("Single Match Over-wise View")

    mv = filtered.copy().sort_values(["innings", "over"])

    mv["Runs in Over"] = mv["runs_in_over"]
    mv["Wickets in Over"] = mv["wickets_in_over"]
    mv["4s"] = mv["fours"]
    mv["6s"] = mv["sixes"]

    # Runs
    fig_runs = px.bar(
        mv,
        x="over",
        y="Runs in Over",
        color="batting_order",
        title="Runs in Each Over",
        hover_data=[
            "match_no", "venue", "batting_team",
            "bowling_team", "batting_order",
            "over", "Runs in Over", "Wickets in Over", "4s", "6s"
        ]
    )
    fig_runs.update_xaxes(dtick=1)
    st.plotly_chart(fig_runs, use_container_width=True)

    # Boundaries
    b = mv.melt(
        id_vars=["over", "batting_order", "Runs in Over", "Wickets in Over"],
        value_vars=["4s", "6s"],
        var_name="Type",
        value_name="Count"
    )

    fig_boundaries = px.bar(
        b,
        x="over",
        y="Count",
        color="Type",
        title="4s and 6s in Each Over",
        hover_data=["over", "Type", "Count", "Runs in Over", "Wickets in Over"]
    )
    fig_boundaries.update_xaxes(dtick=1)
    st.plotly_chart(fig_boundaries, use_container_width=True)

    # Wickets
    fig_wkts = px.bar(
        mv,
        x="over",
        y="Wickets in Over",
        color="batting_order",
        title="Wickets in Each Over",
        hover_data=["over", "Wickets in Over", "Runs in Over", "4s", "6s"]
    )
    fig_wkts.update_xaxes(dtick=1)
    st.plotly_chart(fig_wkts, use_container_width=True)

    # Table
    st.subheader("Over-wise Table")
    st.dataframe(mv, use_container_width=True)

else:
    st.info("Select a single match to view over-wise charts.")

# ================================
# SELECTED OVER ANALYSIS
# ================================
st.subheader("Selected Over Analysis")

if selected_over != "All":

    ov = filtered[filtered["over"] == selected_over]

    st.write(f"Matches: {ov['match_no'].nunique()}")
    st.write(f"Runs: {ov['runs_in_over'].sum()}")
    st.write(f"Wickets: {ov['wickets_in_over'].sum()}")

    st.dataframe(ov, use_container_width=True)

else:
    st.info("Select an over to analyze.")