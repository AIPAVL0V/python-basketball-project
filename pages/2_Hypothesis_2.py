import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from scipy.stats import pearsonr, spearmanr
from pathlib import Path


st.set_page_config(
    page_title="Hypothesis 2",
    layout="wide"
)


st.title("Hypothesis 2")
st.subheader("3-Point Shooting Efficiency and Winning Percentage")


st.markdown("""
## Research Question

Does a team's 3-point shooting percentage correlate with its winning percentage over an NBA season?

## Hypothesis

Teams with a higher 3-point field goal percentage tend to have a higher winning percentage during the regular season.

As the NBA has evolved toward perimeter-oriented play, the ability to efficiently shoot three-pointers has become
a significant factor in team success. We expect a positive correlation between season-average 3PT% and win percentage.

## Key Variables

### Explanatory Variable

* Average 3-point field goal percentage per season (`avg_fg3_pct`)

### Response Variable

* Winning percentage per season (`win_pct`)
""")


st.markdown("---")


st.markdown("""
## Loading the data

The main source is `data/processed/game.csv`, which contains one row per team per game.

Only **Regular Season** games were kept. The three-point line was introduced in the NBA in the **1979–80 season**,
so all seasons before 1979 were excluded.
""")

st.code("""
game_path = Path("..") / "data" / "processed" / "game.csv"
games = pd.read_csv(game_path)

games = games[games["season_type"] == "Regular Season"]
games["season"] = games["season_id"].astype(str).str[1:].astype(int)
games = games[games["season"] >= 1979]
""", language="python")


st.markdown("""
## Building team-season statistics

Each game row contains both home and away team data. To get one row per team per game,
the home and away sides were separated and then stacked.

Each team-season group was aggregated into:

- `avg_fg3_pct` — average 3-point field goal percentage across all games that season
- `wins` — total wins
- `total_games` — total games played
- `win_pct` — wins / total games
""")

st.code("""
home = games[["season", "team_abbreviation_home", "fg3_pct_home", "wl_home"]].rename(columns={
    "team_abbreviation_home": "team",
    "fg3_pct_home": "fg3_pct",
    "wl_home": "wl"
})
away = games[["season", "team_abbreviation_away", "fg3_pct_away", "wl_away"]].rename(columns={
    "team_abbreviation_away": "team",
    "fg3_pct_away": "fg3_pct",
    "wl_away": "wl"
})
team_games = pd.concat([home, away], ignore_index=True)
team_games["win"] = (team_games["wl"] == "W").astype(int)

team_season = team_games.groupby(["season", "team"]).agg(
    avg_fg3_pct=("fg3_pct", "mean"),
    wins=("win", "sum"),
    total_games=("win", "count")
).reset_index()
team_season["win_pct"] = team_season["wins"] / team_season["total_games"]
""", language="python")


st.markdown("""
## Saving and loading the final table

The result was saved to `data/app/team_season_stats.csv` so the page loads quickly
without re-processing the full 22 MB game file every time.
""")

st.code("""
team_season.to_csv("../data/app/team_season_stats.csv", index=False)
""", language="python")


st.markdown("---")


@st.cache_data
def load_data():
    data_path = Path("data/app/team_season_stats.csv")
    if not data_path.exists():
        return None
    return pd.read_csv(data_path)


team_season = load_data()


st.markdown("## Final dataset")

if team_season is None:
    st.error("""
    The file `data/app/team_season_stats.csv` was not found.

    Run the notebook first and save the table using:

    ```
    team_season.to_csv("../data/app/team_season_stats.csv", index=False)
    ```
    """)
    st.stop()

st.write("Below is the aggregated team-season table used for this analysis.")
st.dataframe(team_season.head(20))


st.markdown("""
## Correlation analysis

To test the hypothesis, two correlation tests were performed between `avg_fg3_pct` and `win_pct`:

- **Pearson** — measures the linear relationship
- **Spearman** — measures the monotonic relationship (more robust to outliers)
""")

st.code("""
pearson_r, pearson_p   = pearsonr(team_season["avg_fg3_pct"], team_season["win_pct"])
spearman_r, spearman_p = spearmanr(team_season["avg_fg3_pct"], team_season["win_pct"])
""", language="python")

temp = team_season[["avg_fg3_pct", "win_pct"]].dropna()
pearson_r, pearson_p   = pearsonr(temp["avg_fg3_pct"], temp["win_pct"])
spearman_r, spearman_p = spearmanr(temp["avg_fg3_pct"], temp["win_pct"])

col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    st.metric("Pearson r", f"{pearson_r:.4f}")
with col2:
    st.metric("Pearson p-value", f"{pearson_p:.2e}")
with col3:
    st.metric("Spearman r", f"{spearman_r:.4f}")
with col4:
    st.metric("Spearman p-value", f"{spearman_p:.2e}")
with col5:
    st.metric("Observations", len(temp))


st.markdown("""
## Scatter plot: 3PT% vs Win%

Each dot represents one team in one season. The regression line shows the overall trend.
""")

fig1, ax1 = plt.subplots(figsize=(10, 6))
sns.regplot(
    x="avg_fg3_pct",
    y="win_pct",
    data=team_season,
    scatter_kws={"alpha": 0.5},
    ax=ax1
)
ax1.set_title("3-Point Shooting % vs Winning % (Team-Season)")
ax1.set_xlabel("Average 3PT%")
ax1.set_ylabel("Winning %")
ax1.grid(True)
fig1.tight_layout()
st.pyplot(fig1)


st.markdown("""
## Top 10 teams by 3PT% vs the rest

Each season, teams were ranked by their average 3-point percentage.
The top 10 were compared against all remaining teams to see whether better shooting translates to more wins.
""")

def label_group(group_df):
    sorted_df = group_df.sort_values("avg_fg3_pct", ascending=False)
    result = pd.Series("Rest", index=sorted_df.index)
    result.iloc[:10] = "Top 10 (3PT%)"
    return result

team_season_grouped = team_season.copy()
team_season_grouped["group"] = team_season_grouped.groupby("season", group_keys=False).apply(label_group)

group_trend = (
    team_season_grouped
    .groupby(["season", "group"])["win_pct"]
    .mean()
    .reset_index()
)

fig3, ax3 = plt.subplots(figsize=(13, 6))

for group, color, ls in [("Top 10 (3PT%)", "tab:green", "-"), ("Rest", "tab:gray", "--")]:
    data = group_trend[group_trend["group"] == group]
    ax3.plot(data["season"], data["win_pct"], color=color, linestyle=ls,
             marker="o", markersize=4, label=group)

ax3.axhline(0.5, color="black", linewidth=0.8, linestyle=":", alpha=0.5, label="0.500 baseline")
ax3.set_xlabel("Season")
ax3.set_ylabel("Average Win%")
ax3.set_title("Win% — Top 10 Teams by 3PT% vs Rest (per season)")
ax3.legend()
ax3.grid(True, alpha=0.3)
fig3.tight_layout()
st.pyplot(fig3)

top10_avg = group_trend[group_trend["group"] == "Top 10 (3PT%)" ]["win_pct"].mean()
rest_avg  = group_trend[group_trend["group"] == "Rest"]["win_pct"].mean()

col1, col2, col3 = st.columns(3)
col1.metric("Top 10 avg Win%", f"{top10_avg:.1%}")
col2.metric("Rest avg Win%",   f"{rest_avg:.1%}")
col3.metric("Gap", f"+{top10_avg - rest_avg:.1%}")


st.markdown("""
## Conclusion

Both the Pearson and Spearman correlation tests indicate a **statistically significant positive correlation**
between a team's average 3-point shooting percentage and its winning percentage during the regular season.

The scatter plot confirms a positive linear relationship across all team-seasons since 1979.

The group comparison chart makes the effect concrete: teams in the **top 10 by 3PT%** each season win
roughly **~57%** of their games on average, while the rest of the league wins only **~46%** —
a gap of about **10 percentage points** that is consistent across decades.

**The hypothesis is confirmed**: teams that shoot more efficiently from beyond the arc tend to win
significantly more games in the NBA regular season.

It is worth noting that correlation does not imply causation — teams that are already strong may also happen
to have better shooters, and other variables (defense, home-court advantage, schedule) also influence win rates.
""")
