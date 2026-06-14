# Python Basketball Data Analysis Project

## Project Description

This project is a Python data analysis project focused on basketball statistics.
The main goal of the project is to explore basketball data, test hypotheses, and identify possible relationships between player characteristics, team performance, and statistical results.

The project uses a basketball dataset from Kaggle and includes data loading, exploratory data analysis, basic statistical analysis, and data visualization.

## Dataset

The dataset used in this project is taken from Kaggle:

**Basketball Dataset:**
https://www.kaggle.com/datasets/wyattowalsh/basketball

The dataset contains basketball-related data, including information about players, teams, games, and statistics.

The dataset files are stored locally in the following folder:

**Processed files**
https://drive.google.com/drive/folders/1g4MZedouQvNmU36uG173ceIktg0ezUFF?usp=sharing

```text
data/raw/
```

The main dataset files used in this project are:

```text
nba.sqlite
synthetic_basketball_dataset.csv
```

> Note: The dataset files are not uploaded to GitHub because the `data/` folder is ignored in `.gitignore`.

## Research Questions and Hypotheses

This project focuses on two main research areas: player development and team shooting efficiency.

### Hypothesis 1

Pre-draft player characteristics influence future NBA performance.

This hypothesis examines whether factors before the NBA Draft are related to a player's future productivity in the NBA.

Possible pre-draft factors may include:

* College statistics
* Draft position
* Player age
* Height and weight
* Position
* Pre-draft performance indicators

Possible future NBA performance indicators may include:

* Points per game
* Assists per game
* Rebounds per game
* Minutes played
* Player efficiency
* Career longevity

### Hypothesis 2

Teams with a higher three-point shooting percentage tend to have a higher winning percentage during the season.

This hypothesis examines whether teams that shoot more efficiently from the three-point line are more likely to win games and achieve better season results.

Possible indicators for this hypothesis may include:

* Three-point shooting percentage
* Number of wins
* Number of losses
* Winning percentage
* Points per game
* Team offensive efficiency

## Project Structure

```text
python-basketball-project/
│
├── data/
│   ├── raw/                              # Raw dataset files
│   ├── processed/                        # Cleaned data (game.csv, etc.)
│   └── app/                              # Lightweight CSVs for the dashboard
│       ├── team_season_stats.csv         # Team stats per season (Hypothesis 2)
│       └── team_stats.csv               # All-time team stats (Team Search)
│
├── notebooks/
│   ├── exploratory_analysis.ipynb        # Exploratory data analysis
│   ├── data_processing.ipynb             # Data cleaning pipeline
│   └── hypothesis_3pt-wins.ipynb         # Hypothesis 2 analysis + data export
│
├── pages/                                # Streamlit multi-page app
│   ├── 1_Hypothesis_1.py                 # Hypothesis 1 page (partner)
│   ├── 2_Hypothesis_2.py                 # Hypothesis 2 page (3PT% vs Win%)
│   ├── 3_Player_Search.py                # Player search stub (in progress)
│   └── 4_Team_Search.py                  # Team search page (uses FastAPI)
│
├── reports/
│   └── final_report.md                   # Final project report
│
├── src/
│   ├── analysis.py                       # Analysis functions
│   ├── data_cleaning.py                  # Data cleaning functions
│   └── data_loading.py                   # Data loading functions
│
├── app.py                                # Streamlit main page
├── api.py                                # FastAPI backend (GET /team)
├── main.py                               # Entry point placeholder
├── requirements.txt                      # Required Python libraries
├── README.md                             # Project description
├── LICENSE                               # Project license
└── .gitignore                            # Ignored files and folders
```

## Technologies Used

The project uses the following technologies and libraries:

* Python
* Pandas
* NumPy
* Matplotlib
* Seaborn
* Jupyter Notebook
* SQLite
* Scikit-learn

## Installation

To run this project locally, follow these steps.

### 1. Clone the repository

```bash
git clone https://github.com/AIPAVL0V/python-basketball-project.git
```

### 2. Go to the project folder

```bash
cd python-basketball-project
```

### 3. Create a virtual environment

```bash
python -m venv .venv
```

### 4. Activate the virtual environment

For Windows:

```bash
.venv\Scripts\Activate
```

### 5. Install the required libraries

```bash
pip install -r requirements.txt
```

## How to Run the Project

### Notebooks

Open Jupyter Notebook:

```bash
jupyter notebook
```

Then open the following file:

```text
notebooks/exploratory_analysis.ipynb
```

This notebook contains the main exploratory data analysis and hypothesis testing.

### Streamlit dashboard + FastAPI

The interactive dashboard requires two processes running simultaneously — open two terminal windows.

**Terminal 1 — start the API server:**

```bash
uvicorn api:app --reload --port 8000
```

**Terminal 2 — start the Streamlit app:**

```bash
streamlit run app.py
```

The dashboard will open automatically at `http://localhost:8501`.  
The Team Search page communicates with the API at `http://127.0.0.1:8000`.

> Make sure `data/app/team_season_stats.csv` and `data/app/team_stats.csv` exist before launching.  
> If they are missing, run `notebooks/hypothesis_3pt-wins.ipynb` first.

## Project Workflow

The project follows these main steps:

1. Load the dataset
2. Explore the structure of the data
3. Clean and prepare the data
4. Analyze player and team statistics
5. Test the research hypotheses
6. Create visualizations
7. Write conclusions based on the results

## Current Progress

* GitHub repository created
* Project structure prepared
* Virtual environment configured
* Required Python libraries installed
* Dataset downloaded and added locally
* Initial exploratory analysis started
* Research hypotheses defined

## Expected Results

The project is expected to show whether there are meaningful relationships between:

* Pre-draft player characteristics and future NBA performance
* Team three-point shooting percentage and winning percentage

The final results will be presented using tables, charts, and written conclusions.

## Authors

Alexander Pavlov 
Ivan Zhbanov

## License

This project is licensed under the MIT License.
