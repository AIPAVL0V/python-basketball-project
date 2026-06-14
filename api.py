from fastapi import FastAPI, HTTPException
from pathlib import Path
import pandas as pd

app = FastAPI(title="Basketball API")

TEAM_STATS = pd.read_csv(Path(__file__).parent / "data/app/team_stats.csv")


@app.get("/team")
def get_team(name: str):
    """Return aggregate stats for a team by abbreviation or full name (case-insensitive)."""
    q = name.strip().lower()
    df = TEAM_STATS[
        TEAM_STATS["team"].str.lower().eq(q)
        | TEAM_STATS["name"].str.lower().str.contains(q, regex=False)
    ]
    if df.empty:
        raise HTTPException(status_code=404, detail="Team not found")
    row = df.iloc[0].to_dict()
    return {k: (None if pd.isna(v) else v) for k, v in row.items()}
