from fastapi import FastAPI, HTTPException
from pathlib import Path
import pandas as pd
from scipy.stats import pearsonr


app = FastAPI(title="Basketball API")


BASE_DIR = Path(__file__).parent

PLAYER_STATS_PATH = BASE_DIR / "data/app/player_stats.csv"
TEAM_STATS_PATH = BASE_DIR / "data/app/team_stats.csv"


def clean_record(record: dict):
    return {
        key: None if pd.isna(value) else value
        for key, value in record.items()
    }


def load_player_stats():
    if not PLAYER_STATS_PATH.exists():
        raise HTTPException(
            status_code=404,
            detail="data/app/player_stats.csv was not found"
        )

    return pd.read_csv(PLAYER_STATS_PATH)


def load_team_stats():
    if not TEAM_STATS_PATH.exists():
        raise HTTPException(
            status_code=404,
            detail="data/app/team_stats.csv was not found"
        )

    return pd.read_csv(TEAM_STATS_PATH)


@app.get("/")
def root():
    return {
        "message": "Basketball API is running",
        "endpoints": [
            "/players",
            "/players/search",
            "/columns/numeric",
            "/correlation",
            "/team"
        ]
    }


@app.get("/players")
def get_players(limit: int = 20, offset: int = 0):
    players = load_player_stats()

    result = players.iloc[offset:offset + limit]

    return {
        "limit": limit,
        "offset": offset,
        "total_rows": len(players),
        "data": [
            clean_record(row)
            for row in result.to_dict(orient="records")
        ]
    }


@app.get("/players/search")
def search_players(name: str, limit: int = 20):
    players = load_player_stats()

    if "player_name" not in players.columns:
        raise HTTPException(
            status_code=400,
            detail="Column player_name was not found"
        )

    result = players[
        players["player_name"].str.contains(name, case=False, na=False)
    ].head(limit)

    return {
        "query": name,
        "count": len(result),
        "data": [
            clean_record(row)
            for row in result.to_dict(orient="records")
        ]
    }


@app.get("/columns/numeric")
def get_numeric_columns():
    players = load_player_stats()

    numeric_columns = players.select_dtypes(include="number").columns.tolist()

    return {
        "numeric_columns": numeric_columns
    }


@app.get("/correlation")
def calculate_correlation(x_col: str, y_col: str):
    players = load_player_stats()

    if x_col not in players.columns:
        raise HTTPException(
            status_code=400,
            detail=f"Column {x_col} was not found"
        )

    if y_col not in players.columns:
        raise HTTPException(
            status_code=400,
            detail=f"Column {y_col} was not found"
        )

    temp = players[[x_col, y_col]].dropna()

    if len(temp) < 2:
        raise HTTPException(
            status_code=400,
            detail="Not enough observations to calculate correlation"
        )

    corr, p_value = pearsonr(temp[x_col], temp[y_col])

    return {
        "x_col": x_col,
        "y_col": y_col,
        "correlation": corr,
        "p_value": p_value,
        "observations": len(temp),
        "data": [
            clean_record(row)
            for row in temp.to_dict(orient="records")
        ]
    }


@app.get("/team")
def get_team(name: str):
    team_stats = load_team_stats()

    q = name.strip().lower()

    df = team_stats[
        team_stats["team"].str.lower().eq(q)
        | team_stats["name"].str.lower().str.contains(q, regex=False)
    ]

    if df.empty:
        raise HTTPException(status_code=404, detail="Team not found")

    row = df.iloc[0].to_dict()

    return clean_record(row)