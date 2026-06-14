import streamlit as st

st.set_page_config(
    page_title="NBA Analytics",
    page_icon="🏀",
    layout="wide"
)

st.title("🏀 NBA Analytics")
st.subheader("Exploring NBA data through hypotheses and team statistics")

st.markdown("""
Welcome to the NBA Analytics dashboard. This project analyses historical NBA game data
to test hypotheses about player performance and team success.

Use the sidebar to navigate between pages.
""")

st.markdown("---")

st.markdown("""
## Pages

### Hypothesis 1 — Pre-Draft Background and NBA Performance
Investigates whether a player's pre-draft characteristics (draft position, physical measurements)
predict their NBA career performance in points, assists, and rebounds.

### Hypothesis 2 — 3-Point Shooting and Winning
Tests whether a team's 3-point field goal percentage correlates with its winning percentage
across NBA regular seasons since 1979.

### Player Search
Search for individual players and view their draft information, physical measurements, and NBA performance metrics.  
The page also allows users to compare two numerical variables, calculate Pearson correlation, and visualize the relationship with a scatter plot.

### Team Search
Look up all-time aggregate statistics for any NBA team by abbreviation or full name.
Powered by the FastAPI backend (`GET /team`).
""")

st.markdown("---")

st.markdown("""
## Data source

All data comes from the [NBA dataset on Kaggle](https://www.kaggle.com/datasets/wyattowalsh/basketball),
processed from `data/processed/game.csv`.
Heavy preprocessing is done once in the notebooks; the Streamlit pages read only
the lightweight CSV files from `data/app/`.
""")
