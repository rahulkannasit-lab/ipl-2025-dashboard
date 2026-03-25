import pandas as pd
import streamlit as st
import plotly.express as px

# ================================
# PAGE CONFIG
# ================================
st.set_page_config(page_title="IPL 2025 Over-wise Dashboard", layout="wide")

# ================================
# LOAD DATA
# ================================
DATA_FILE = "ipl2025_over_summary.csv"
df = pd.read_csv(DATA_FILE)

# ================================
# CLEAN DATA
# ================================
df["batting_order"] = df["innings"].apply(
    lambda x: "First Batting" if x == 1 else "Second Batting"
)

df["over"] = pd.to_numeric(df["over"], errors="coerce")
df = df.dropna(subset=["over"]).copy()
df["over"] = df["over"].astype(int)

# If overs are 0-19, convert to 1-20
if df["over"].min() == 0 and df["over"].max() <= 19:
    df["over"] = df["over"] + 1

# ================================
# TITLE
# ================================
st.title("🏏 IPL 2025 Over-wise Dashboard")
st.caption("Analyze runs, wickets, 4s and 6s by over using team, opposition, match, venue and batting-order filters.")

# ================================
# FILTERS - TOP OF PAGE
# ================================
st.subheader("Filters")

teams = ["All"] + sorted(df["batting_team"].dropna().unique().tolist())
venues = ["All"] + sorted(df["venue"].dropna().unique().tolist())
matches = ["All"] + sorted(df["match_no"].dropna().unique().tolist())
overs = ["All"] + sorted(df["over"].dropna().unique().tolist())
batting_orders = ["All", "First Batting", "Second Batting"]

f1, f2 = st.columns(2)
selected_team = f1.selectbox("Batting Team", teams)
selected_opposition = f2.selectbox("Opposition", teams)

f3, f4 = st.columns(2)
selected_match = f3.selectbox("Match", matches)
selected_over = f4.selectbox("Over", overs)

f5, f6 = st.columns(2)
selected_venue = f5.selectbox("Venue", venues)
selected_batting_order = f6.selectbox("Batting Order", batting_orders)

# ================================
# FILTER FUNCTION
# ================================
def apply_filters(dataframe):
    temp = dataframe.copy()

    if selected_team != "All":
        temp = temp[temp["batting_team"] == selected_team]

    if selected_opposition != "All":
        temp = temp[temp["bowling_team"] == selected_opposition]

    if selected_match != "All":
        temp = temp[temp["match_no"] == selected_match]

    if selected_over != "All":
        temp = temp[temp["over"] == selected_over]

    if selected_venue != "All":
        temp = temp[temp["venue"] == selected_venue]

    if selected_batting_order != "All":
        temp = temp[temp["batting_order"] == selected_batting_order]

    return temp

filtered = apply_filters(df).sort_values(["match_no", "innings", "over"]).reset_index(drop=True)

# ================================
# KPI SUMMARY
# ================================
st.subheader("Summary")

k1, k2, k3, k4, k5 = st.columns(5)
k1.metric("Matches", int(filtered["match_no"].nunique()) if not filtered.empty else 0)
k2.metric("Runs", int(filtered["runs_in_over"].sum()) if not filtered.empty else 0)
k3.metric("Wickets", int(filtered["wickets_in_over"].sum()) if not filtered.empty else 0)
k4.metric("4s", int(filtered["fours"].sum()) if not filtered.empty else 0)
k5.metric("6s", int(filtered["sixes"].sum()) if not filtered.empty else 0)

# ================================
# SINGLE MATCH VIEW
# ================================
single_match_selected = filtered["match_no"].nunique() == 1

if single_match_selected and not filtered.empty:
    st.subheader("Single Match Over-wise View")

    match_view = filtered.copy().sort_values(["innings", "over"]).reset_index(drop=True)

    match_view["Runs in Over"] = match_view["runs_in_over"]
    match_view["Wickets in Over"] = match_view["wickets_in_over"]
    match_view["4s"] = match_view["fours"]
    match_view["6s"] = match_view["sixes"]

    # Runs in each over
    fig_runs = px.bar(
        match_view,
        x="over",
        y="Runs in Over",
        color="batting_order",
        barmode="group",
        title="Runs in Each Over",
        hover_data=[
            "match_no",
            "venue",
            "batting_team",
            "bowling_team",
            "batting_order",
            "over",
            "Runs in Over",
            "Wickets in Over",
            "4s",
            "6s",
        ],
    )
    fig_runs.update_xaxes(dtick=1)
    fig_runs.update_layout(height=420)
    st.plotly_chart(fig_runs, use_container_width=True)

    # 4s and 6s in each over
    boundary_view = match_view.melt(
        id_vars=[
            "match_no",
            "venue",
            "batting_team",
            "bowling_team",
            "batting_order",
            "over",
            "Runs in Over",
            "Wickets in Over",
        ],
        value_vars=["4s", "6s"],
        var_name="Boundary Type",
        value_name="Count",
    )

    fig_boundaries = px.bar(
        boundary_view,
        x="over",
        y="Count",
        color="Boundary Type",
        barmode="group",
        title="4s and 6s in Each Over",
        hover_data=[
            "match_no",
            "venue",
            "batting_team",
            "bowling_team",
            "batting_order",
            "over",
            "Boundary Type",
            "Count",
            "Runs in Over",
            "Wickets in Over",
        ],
    )
    fig_boundaries.update_xaxes(dtick=1)
    fig_boundaries.update_layout(height=420)
    st.plotly_chart(fig_boundaries, use_container_width=True)

    # Wickets in each over
    fig_wkts = px.bar(
        match_view,
        x="over",
        y="Wickets in Over",
        color="batting_order",
        barmode="group",
        title="Wickets in Each Over",
        hover_data=[
            "match_no",
            "venue",
            "batting_team",
            "bowling_team",
            "batting_order",
            "over",
            "Runs in Over",
            "Wickets in Over",
            "4s",
            "6s",
        ],
    )
    fig_wkts.update_xaxes(dtick=1)
    fig_wkts.update_layout(height=420)
    st.plotly_chart(fig_wkts, use_container_width=True)

    st.subheader("Single Match Over-level Table")
    single_match_cols = [
        "match_no",
        "venue",
        "innings",
        "batting_order",
        "batting_team",
        "bowling_team",
        "over",
        "runs_in_over",
        "wickets_in_over",
        "fours",
        "sixes",
        "cumulative_runs",
        "cumulative_wkts",
        "score_after_over",
    ]
    st.dataframe(match_view[single_match_cols], use_container_width=True)

elif selected_match == "All":
    st.info("Select a single match to view over-wise charts for that match.")

# ================================
# SELECTED OVER ANALYSIS
# ================================
st.subheader("Selected Over Analysis")

if selected_over == "All":
    st.info("Select a specific over to view match-by-match over analysis.")
else:
    over_view = filtered.copy()

    if over_view.empty:
        st.warning("No records found for the selected filter combination.")
    else:
        o1, o2, o3, o4, o5 = st.columns(5)
        o1.metric("Over", selected_over)
        o2.metric("Matches", int(over_view["match_no"].nunique()))
        o3.metric("Runs", int(over_view["runs_in_over"].sum()))
        o4.metric("Wickets", int(over_view["wickets_in_over"].sum()))
        o5.metric("4s / 6s", f"{int(over_view['fours'].sum())} / {int(over_view['sixes'].sum())}")

        over_view = over_view.sort_values(
            ["runs_in_over", "fours", "sixes", "match_no"],
            ascending=[False, False, False, True],
        )

        table_cols = [
            "match_no",
            "venue",
            "innings",
            "batting_order",
            "batting_team",
            "bowling_team",
            "over",
            "runs_in_over",
            "wickets_in_over",
            "fours",
            "sixes",
            "score_after_over",
        ]
        st.dataframe(over_view[table_cols], use_container_width=True)

# ================================
# FULL FILTERED TABLE
# ================================
with st.expander("Show Full Filtered Over-level Table"):
    full_table_cols = [
        "match_no",
        "venue",
        "innings",
        "batting_order",
        "batting_team",
        "bowling_team",
        "over",
        "runs_in_over",
        "wickets_in_over",
        "fours",
        "sixes",
        "cumulative_runs",
        "cumulative_wkts",
        "score_after_over",
    ]
    st.dataframe(filtered[full_table_cols], use_container_width=True)
