import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import requests


st.set_page_config(
    page_title="Player Search and Correlation",
    layout="wide"
)


API_URL = "https://python-basketball-project.onrender.com"


st.title("Player Search and Correlation")
st.subheader("FastAPI-powered player search and correlation analysis")


def get_players(limit=20, offset=0):
    response = requests.get(
        f"{API_URL}/players",
        params={
            "limit": limit,
            "offset": offset
        }
    )

    if response.status_code != 200:
        return None

    return response.json()


def get_numeric_columns():
    response = requests.get(f"{API_URL}/columns/numeric")

    if response.status_code != 200:
        return []

    return response.json()["numeric_columns"]


def get_correlation(x_col, y_col):
    response = requests.get(
        f"{API_URL}/correlation",
        params={
            "x_col": x_col,
            "y_col": y_col
        }
    )

    if response.status_code != 200:
        return None, response.json().get("detail", "Unknown error")

    return response.json(), None


def search_players(name, limit=10):
    response = requests.get(
        f"{API_URL}/players/search",
        params={
            "name": name,
            "limit": limit
        }
    )

    if response.status_code != 200:
        return None

    return response.json()


st.markdown("---")


try:
    api_check = requests.get(f"{API_URL}/")
except requests.exceptions.ConnectionError:
    st.error("""
    FastAPI server is not running.

    Start it in a separate terminal with:

    uvicorn api:app --reload
    """)
    st.stop()


if api_check.status_code != 200:
    st.error("FastAPI server is not responding correctly.")
    st.stop()


st.success("FastAPI server is running.")


st.markdown("## Correlation analysis")

st.write("""
Choose two numerical variables and calculate Pearson correlation between them.
The calculation is performed by the FastAPI backend.
""")

numeric_columns = get_numeric_columns()

if len(numeric_columns) < 2:
    st.error("Not enough numeric columns for correlation analysis.")
    st.stop()


col1, col2 = st.columns(2)

with col1:
    default_x = numeric_columns.index("overall_pick") if "overall_pick" in numeric_columns else 0

    x_col = st.selectbox(
        "Choose first variable",
        numeric_columns,
        index=default_x
    )

with col2:
    default_y = numeric_columns.index("pts_per_game") if "pts_per_game" in numeric_columns else 1

    y_col = st.selectbox(
        "Choose second variable",
        numeric_columns,
        index=default_y
    )


if st.button("Calculate correlation"):
    correlation_result, error = get_correlation(x_col, y_col)

    if error:
        st.error(error)
    else:
        corr = correlation_result["correlation"]
        p_value = correlation_result["p_value"]
        observations = correlation_result["observations"]

        data = pd.DataFrame(correlation_result["data"])

        metric_col1, metric_col2, metric_col3 = st.columns(3)

        with metric_col1:
            st.metric("Correlation", f"{corr:.4f}")

        with metric_col2:
            st.metric("P-value", f"{p_value:.4f}")

        with metric_col3:
            st.metric("Observations", observations)

        fig, ax = plt.subplots(figsize=(8, 5))

        ax.scatter(
            data[x_col],
            data[y_col],
            alpha=0.6
        )

        ax.set_title(f"{x_col} vs {y_col}")
        ax.set_xlabel(x_col)
        ax.set_ylabel(y_col)
        ax.grid(True)

        st.pyplot(fig)

        st.markdown("### Interpretation")

        if corr > 0:
            st.write(
                "The correlation is positive. When one variable increases, "
                "the other variable also tends to increase."
            )
        elif corr < 0:
            st.write(
                "The correlation is negative. When one variable increases, "
                "the other variable tends to decrease."
            )
        else:
            st.write("The correlation is close to zero.")

        if abs(corr) < 0.2:
            st.info("The relationship is weak.")
        elif abs(corr) < 0.5:
            st.warning("The relationship is moderate.")
        else:
            st.success("The relationship is strong.")

        if p_value < 0.05:
            st.success("The p-value is below 0.05, so the relationship is statistically significant.")
        else:
            st.warning("The p-value is above 0.05, so the relationship is not statistically significant.")


st.markdown("---")


st.markdown("## Player search")

st.write("""
Search for a player by name.  
The search is performed through the FastAPI endpoint `/players/search`.
""")

search_query = st.text_input(
    "Enter player name",
    placeholder="Example: LeBron James"
)


if search_query:
    search_result = search_players(search_query, limit=20)

    if search_result is None:
        st.error("Could not search players.")
    elif search_result["count"] == 0:
        st.warning("No players found.")
    else:
        found_players = pd.DataFrame(search_result["data"])

        st.write(f"Found players: **{search_result['count']}**")

        player_options = found_players["player_name"].dropna().unique().tolist()

        selected_player = st.selectbox(
            "Choose player",
            player_options
        )

        selected_rows = found_players[
            found_players["player_name"] == selected_player
        ]

        player = selected_rows.iloc[0]

        st.markdown(f"## {selected_player}")

        info_col1, info_col2, info_col3 = st.columns(3)

        with info_col1:
            st.markdown("### Draft information")

            if "season" in player.index:
                st.write(f"**Draft season:** {player['season']}")

            if "overall_pick" in player.index:
                st.write(f"**Overall pick:** {player['overall_pick']}")

            if "organization" in player.index:
                st.write(f"**Organization:** {player['organization']}")

            if "organization_type" in player.index:
                st.write(f"**Organization type:** {player['organization_type']}")

        with info_col2:
            st.markdown("### Physical measurements")

            if "height_wo_shoes" in player.index:
                st.write(f"**Height without shoes:** {player['height_wo_shoes']}")

            if "weight" in player.index:
                st.write(f"**Weight:** {player['weight']}")

            if "wingspan" in player.index:
                st.write(f"**Wingspan:** {player['wingspan']}")

            if "bmi" in player.index:
                if pd.notna(player["bmi"]):
                    st.write(f"**BMI:** {player['bmi']:.2f}")
                else:
                    st.write("**BMI:** missing")

        with info_col3:
            st.markdown("### NBA performance")

            if "pts_per_game" in player.index:
                if pd.notna(player["pts_per_game"]):
                    st.write(f"**Points per game:** {player['pts_per_game']:.2f}")
                else:
                    st.write("**Points per game:** missing")

            if "assists_per_game" in player.index:
                if pd.notna(player["assists_per_game"]):
                    st.write(f"**Assists per game:** {player['assists_per_game']:.2f}")
                else:
                    st.write("**Assists per game:** missing")

            if "rebounds_per_game" in player.index:
                if pd.notna(player["rebounds_per_game"]):
                    st.write(f"**Rebounds per game:** {player['rebounds_per_game']:.2f}")
                else:
                    st.write("**Rebounds per game:** missing")

        st.markdown("### Full player data")
        st.dataframe(selected_rows)