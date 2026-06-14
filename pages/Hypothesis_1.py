import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from scipy.stats import pearsonr

def correlation_plot(df, x_col, y_col, method="pearson"):
    temp = df[[x_col, y_col]].dropna()

    corr, p_value = pearsonr(temp[x_col], temp[y_col])

    fig, ax = plt.subplots(figsize=(8, 5))

    ax.scatter(temp[x_col], temp[y_col], alpha=0.6)

    ax.set_title(f"{x_col} vs {y_col}")
    ax.set_xlabel(x_col)
    ax.set_ylabel(y_col)
    ax.grid(True)

    return corr, p_value, len(temp), fig

