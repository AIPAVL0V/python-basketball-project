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
## League-wide trend over seasons

The chart below shows how the league-average 3PT% and win% have evolved over time.
Both axes are independent so the trends can be compared visually.
""")

season_trend = team_season.groupby("season").agg(
    avg_fg3_pct=("avg_fg3_pct", "mean"),
    avg_win_pct=("win_pct", "mean")
).reset_index()

fig2, ax_left = plt.subplots(figsize=(12, 6))

ax_left.set_xlabel("Season")
ax_left.set_ylabel("Average 3PT%", color="tab:blue")
ax_left.plot(
    season_trend["season"],
    season_trend["avg_fg3_pct"],
    color="tab:blue", marker="o", markersize=4, label="3PT%"
)
ax_left.tick_params(axis="y", labelcolor="tab:blue")

ax_right = ax_left.twinx()
ax_right.set_ylabel("Average Win%", color="tab:red")
ax_right.plot(
    season_trend["season"],
    season_trend["avg_win_pct"],
    color="tab:red", marker="s", markersize=4, label="Win%"
)
ax_right.tick_params(axis="y", labelcolor="tab:red")

plt.title("League-Wide 3PT% and Win% Trends Over Seasons")
fig2.tight_layout()
st.pyplot(fig2)


st.markdown("""
## Conclusion

Both the Pearson and Spearman correlation tests indicate a **statistically significant positive correlation**
between a team's average 3-point shooting percentage and its winning percentage during the regular season.

The scatter plot confirms a positive linear relationship, and the trend chart shows how the league-wide 3PT%
has steadily increased since the three-point line was introduced in 1979.

**The hypothesis is confirmed**: teams that shoot more efficiently from beyond the arc tend to win more games
in the NBA regular season.

It is worth noting that correlation does not imply causation — teams that are already strong may also happen
to have better shooters, and other variables (defense, home-court advantage, schedule) also influence win rates.
""")
