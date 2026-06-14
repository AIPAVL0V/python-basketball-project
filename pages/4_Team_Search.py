import streamlit as st
import requests

API_URL = "http://127.0.0.1:8000"

st.set_page_config(
    page_title="Team Search",
    layout="wide"
)

st.title("Team Search")
st.subheader("Look up aggregate statistics for any NBA team")

st.markdown("""
Enter a team **abbreviation** (e.g. `LAL`, `GSW`, `BOS`) or part of the **full name**
(e.g. `lakers`, `warriors`) to retrieve all-time statistics from the database.

Statistics are aggregated over all Regular Season games available in the dataset (since 1979).
""")

st.markdown("---")

name = st.text_input("Team name or abbreviation", placeholder="e.g. LAL or lakers")

if name:
    try:
        response = requests.get(f"{API_URL}/team", params={"name": name}, timeout=5)
    except requests.exceptions.ConnectionError:
        st.error(
            "Could not connect to the API. "
            "Make sure the server is running:\n\n"
            "```\nuvicorn api:app --reload --port 8000\n```"
        )
        st.stop()
    except requests.exceptions.Timeout:
        st.error("The API request timed out. Please try again.")
        st.stop()

    if response.status_code == 404:
        st.warning(f'No team found for **"{name}"**. Try a different abbreviation or name.')
        st.stop()

    if response.status_code != 200:
        st.error(f"Unexpected API error (HTTP {response.status_code}).")
        st.stop()

    data = response.json()

    team_abbr = data.get("team", "")
    team_name = data.get("name", "")

    st.markdown(f"## {team_name} ({team_abbr})")
    st.markdown("---")

    # Numeric fields with friendly labels
    FIELD_LABELS = {
        "total_games": ("Total Games", None),
        "wins":        ("Wins",        None),
        "losses":      ("Losses",      None),
        "win_pct":     ("Win %",       ".1%"),
        "avg_pts":     ("Avg Points",  ".1f"),
        "avg_reb":     ("Avg Rebounds",".1f"),
        "avg_ast":     ("Avg Assists", ".1f"),
        "avg_fg3a":    ("Avg 3PA",     ".1f"),
        "avg_fg3_pct": ("Avg 3PT %",   ".1%"),
    }

    # Only show fields that are present and not null in the response
    available = {k: v for k, v in data.items() if k not in ("team", "name") and v is not None}

    if not available:
        st.info("No numeric statistics available for this team.")
        st.stop()

    cols = st.columns(min(len(available), 5))

    for i, (field, value) in enumerate(available.items()):
        label, fmt = FIELD_LABELS.get(field, (field.replace("_", " ").title(), None))
        col = cols[i % len(cols)]
        if fmt and isinstance(value, float):
            if fmt == ".1%":
                col.metric(label, f"{value:.1%}")
            else:
                col.metric(label, f"{value:{fmt}}")
        else:
            col.metric(label, value)
