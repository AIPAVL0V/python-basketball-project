import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from scipy.stats import pearsonr
from pathlib import Path


st.set_page_config(
    page_title="Hypothesis 1",
    layout="wide"
)


st.title("Hypothesis 1")
st.subheader("Pre-Draft Background and NBA Performance")


st.markdown("""
## Research Question

Does a player's pre-draft background influence his performance during his NBA career?

## Hypothesis

Players with stronger pre-draft characteristics and earlier draft positions tend to perform better during their NBA careers.

In this project, pre-draft background includes:

- draft position
- draft round
- college or previous organization
- height
- weight
- wingspan
- BMI

All measurements were taken before the NBA Draft.

Player performance was measured using:

- points per game
- assists per game
- rebounds per game
""")


st.markdown("---")


st.markdown("""
## Loading the data

Two main tables were loaded:

- `draft_history.csv`
- `draft_combine_stats.csv`

The `draft_history.csv` table contains information about NBA draft results.  
The `draft_combine_stats.csv` table contains physical measurements from the draft combine.
""")

st.code("""
draft_history_path = "../data/processed/draft_history.csv"
draft_history = pd.read_csv(draft_history_path)

combine_draft_history_path = "../data/processed/draft_combine_stats.csv"
combine_draft_history = pd.read_csv(combine_draft_history_path)
""", language="python")


st.markdown("""
## Selecting first-round players

Only players drafted in the first round were selected.

This is useful because first-round players are usually evaluated more carefully before the draft.
Therefore, their draft position can be treated as an important pre-draft indicator.
""")

st.code("""
players = draft_history[
    draft_history["round_number"] == 1
][[
    "person_id",
    "player_name",
    "season",
    "overall_pick",
    "organization",
    "organization_type"
]]
""", language="python")


st.markdown("""
## Adding physical measurements

The following physical measurements were added from the draft combine table:

- height without shoes
- weight
- wingspan

After that, BMI was calculated.
""")

st.code("""
combine_draft = combine_draft_history[
    ["player_id", "height_wo_shoes", "weight", "wingspan"]
]

players = players.rename(columns={"person_id": "player_id"})

players = players.merge(
    combine_draft,
    on="player_id",
    how="left"
)

players["weight"] = pd.to_numeric(players["weight"], errors="coerce")

players["bmi"] = (
    players["weight"] * 703 / players["height_wo_shoes"] ** 2
)
""", language="python")


st.markdown("""
## Loading play-by-play data

To calculate NBA performance, the `play_by_play.csv` table was used.

This table contains different events from NBA games, such as:

- made field goals
- free throws
- assists
- rebounds
- substitutions
- period starts
- violations
""")

st.code("""
pbp_path = "../data/processed/play_by_play.csv"
pbp = pd.read_csv(pbp_path)
""", language="python")


st.markdown("""
## Selecting scoring and rebound events

In the play-by-play data, different events have different `eventmsgtype` values.

For this analysis, the following event types were used:

- `eventmsgtype == 1` for made field goals
- `eventmsgtype == 3` for free throws
- `eventmsgtype == 4` for rebounds
""")

st.code("""
field_goals = pbp[pbp["eventmsgtype"] == 1].copy()
free_throws = pbp[pbp["eventmsgtype"] == 3].copy()
rebounds = pbp[pbp["eventmsgtype"] == 4].copy()
""", language="python")


st.markdown("""
## Cleaning event descriptions

Some event descriptions were stored in `homedescription`, while others were stored in `visitordescription`.

Because of this, one common `description` column was created.
The value `"unknown"` was replaced with missing values.
""")

st.code("""
field_goals["description"] = (
    field_goals["homedescription"]
    .replace("unknown", pd.NA)
    .fillna(field_goals["visitordescription"].replace("unknown", pd.NA))
)

free_throws["description"] = (
    free_throws["homedescription"]
    .replace("unknown", pd.NA)
    .fillna(free_throws["visitordescription"].replace("unknown", pd.NA))
)

rebounds["description"] = (
    rebounds["homedescription"]
    .replace("unknown", pd.NA)
    .fillna(rebounds["visitordescription"].replace("unknown", pd.NA))
)
""", language="python")


st.markdown("""
## Calculating points

For made field goals:

- 2 points were assigned for regular field goals
- 3 points were assigned for shots containing `"3PT"` in the description

For free throws, missed attempts were removed and 1 point was assigned for each made free throw.
""")

st.code("""
field_goals["pts"] = 2

field_goals.loc[
    field_goals["description"].str.contains("3PT", na=False),
    "pts"
] = 3

free_throws = free_throws[
    ~free_throws["description"].str.contains("MISS", na=False)
].copy()

free_throws["pts"] = 1
""", language="python")


st.markdown("""
## Creating the scoring events table

After calculating points for field goals and free throws, both tables were combined into one table called `scoring_events`.

This table contains all scoring events and makes it possible to calculate total points for each player.
""")

st.code("""
scoring_events = pd.concat([
    field_goals[["game_id", "player1_id", "player2_id", "pts"]],
    free_throws[["game_id", "player1_id", "pts"]]
], ignore_index=True).sort_values(by="game_id")

rebounds = rebounds[["game_id", "player1_id"]]
""", language="python")


st.markdown("""
## Calculating player points per game

Scoring events were grouped by player and game.

This made it possible to calculate:

- total points
- number of games where the player scored
- points per game
""")

st.code("""
player_game_points = (
    scoring_events
    .groupby(["game_id", "player1_id"])["pts"]
    .sum()
    .reset_index()
)

player_total_points = (
    player_game_points
    .groupby("player1_id")
    .agg(
        total_pts=("pts", "sum"),
        total_games_with_points=("game_id", "nunique")
    )
    .reset_index()
    .rename(columns={"player1_id": "player_id"})
)

player_total_points["pts_per_game"] = (
    player_total_points["total_pts"] /
    player_total_points["total_games_with_points"]
)
""", language="python")


st.markdown("""
## Calculating assists per game

In the scoring events table, `player2_id` represents the assisting player.

This column was used to calculate:

- total assists
- games with assists
- assists per game
""")

st.code("""
player_total_assists = (
    scoring_events[
        scoring_events["player2_id"].notna() &
        (scoring_events["player2_id"] != 0)
    ]
    .groupby("player2_id")
    .agg(
        total_assists=("game_id", "count"),
        total_games_with_assists=("game_id", "nunique")
    )
    .reset_index()
    .rename(columns={"player2_id": "player_id"})
)

player_total_assists["assists_per_game"] = (
    player_total_assists["total_assists"] /
    player_total_assists["total_games_with_assists"]
)

player_total_assists = player_total_assists[
    player_total_assists["player_id"] != 0
]
""", language="python")


st.markdown("""
## Calculating rebounds per game

Rebound events were grouped by player.

This made it possible to calculate:

- total rebounds
- games with rebounds
- rebounds per game
""")

st.code("""
player_total_rebounds = (
    rebounds
    .groupby("player1_id")
    .agg(
        total_rebounds=("game_id", "count"),
        total_games_with_rebounds=("game_id", "nunique")
    )
    .reset_index()
    .rename(columns={"player1_id": "player_id"})
)

player_total_rebounds["rebounds_per_game"] = (
    player_total_rebounds["total_rebounds"] /
    player_total_rebounds["total_games_with_rebounds"]
)
""", language="python")


st.markdown("""
## Merging everything into one final table

After calculating points, assists, and rebounds, all results were merged into the main `players` table.

The final dataset contains both pre-draft characteristics and NBA performance metrics.
""")

st.code("""
players = pd.merge(players, player_total_points, on="player_id", how="left")
players = pd.merge(players, player_total_assists, on="player_id", how="left")
players = pd.merge(players, player_total_rebounds, on="player_id", how="left")
""", language="python")


st.markdown("""
## Saving the final table

The final table was saved as a separate CSV file.

This file is used by the Streamlit page, so the whole preprocessing process does not need to be repeated every time the website is opened.
""")

st.code("""
players.to_csv("../data/app/player_stats.csv", index=False)
""", language="python")


st.markdown("---")


@st.cache_data
def load_final_data():
    data_path = Path("data/app/player_stats.csv")

    if not data_path.exists():
        return None

    return pd.read_csv(data_path)


players = load_final_data()


st.markdown("## Final dataset")

if players is None:
    st.error("""
    The file `data/app/player_stats.csv` was not found.

    Run the notebook first and save the final table using:

    players.to_csv("../data/app/player_stats.csv", index=False)
    """)
    st.stop()


st.write("""
Below is the final table created after all preprocessing steps.
""")

st.dataframe(players.head(20))


st.markdown("""
## Correlation analysis

To test the hypothesis, the correlation between the following variables was calculated:

- `overall_pick`
- `pts_per_game`

A smaller `overall_pick` means that a player was drafted earlier.

For example:

- pick 1 means the player was selected first
- pick 30 means the player was selected later in the first round

Therefore, if earlier draft picks perform better, the expected correlation should be negative.
""")

st.code("""
temp = players[["pts_per_game", "overall_pick"]].dropna()

corr, p_value = pearsonr(
    temp["pts_per_game"],
    temp["overall_pick"]
)
""", language="python")


temp = players[["pts_per_game", "overall_pick"]].dropna()

corr, p_value = pearsonr(
    temp["pts_per_game"],
    temp["overall_pick"]
)

col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Correlation", f"{corr:.4f}")

with col2:
    st.metric("P-value", f"{p_value:.4f}")

with col3:
    st.metric("Observations", len(temp))


fig, ax = plt.subplots(figsize=(8, 5))

ax.scatter(
    temp["pts_per_game"],
    temp["overall_pick"],
    alpha=0.6
)

ax.set_title("Points per Game vs Overall Draft Pick")
ax.set_xlabel("Points per game")
ax.set_ylabel("Overall pick")
ax.grid(True)

st.pyplot(fig)


st.markdown("""
## Interpretation of the result

The correlation is negative.

This means that players with higher points per game usually have lower draft pick numbers.
Since lower draft pick numbers mean earlier selection, the result suggests that players selected earlier in the draft tend to perform better in terms of scoring.

In this analysis, the correlation is approximately **-0.40**.
This can be interpreted as a moderate negative relationship.

The p-value is close to zero, which means that the relationship is statistically significant.
""")


st.markdown("""
## College / organization comparison

Players were also grouped by their college or previous organization.

For each organization, the following values were calculated:

- average points per game
- number of players from that organization

Organizations with only one or two players were filtered out because very small groups can give misleading averages.
""")

st.code("""
org_points = (
    players
    .dropna(subset=["pts_per_game"])
    .groupby("organization")
    .agg(
        avg_pts_per_game=("pts_per_game", "mean"),
        players_count=("player_id", "nunique")
    )
    .reset_index()
    .sort_values("avg_pts_per_game", ascending=False)
)

org_points = org_points[org_points["players_count"] > 2]
""", language="python")


org_points = (
    players
    .dropna(subset=["pts_per_game"])
    .groupby("organization")
    .agg(
        avg_pts_per_game=("pts_per_game", "mean"),
        players_count=("player_id", "nunique")
    )
    .reset_index()
    .sort_values("avg_pts_per_game", ascending=False)
)

org_points = org_points[org_points["players_count"] > 2]

st.dataframe(org_points.head(20))


fig2, ax2 = plt.subplots(figsize=(10, 6))

top_orgs = org_points.head(10).sort_values("avg_pts_per_game")

ax2.barh(
    top_orgs["organization"],
    top_orgs["avg_pts_per_game"]
)

ax2.set_title("Top Organizations by Average Points per Game")
ax2.set_xlabel("Average points per game")
ax2.set_ylabel("Organization")
ax2.grid(axis="x")

st.pyplot(fig2)


st.markdown("""
## Conclusion

The hypothesis is partially supported.

The analysis shows that draft position is related to NBA scoring performance.
Players selected earlier in the draft tend to have higher points per game.

However, the relationship is not perfect.  
A correlation of about **-0.40** means that draft position matters, but it does not fully explain player performance.

Other factors can also influence NBA success, such as:

- injuries
- minutes played
- team role
- coaching system
- player development
- team strength

So, pre-draft background gives useful information, but it cannot fully predict future NBA performance by itself.
""")