"""Generate the static biodiversity forecast chart from repository data."""

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

ROOT_DIR = Path(__file__).resolve().parent
DATA_DIR = ROOT_DIR / "data"
ASSETS_DIR = ROOT_DIR / "assets"


def load_world_history() -> pd.Series:
    biodiv = pd.read_excel(DATA_DIR / "aggregate_exstintion_measure.xlsx")
    pivot = (
        biodiv.pivot_table(
            index=["Country", "Year"],
            columns="VAR",
            values="Value",
            aggfunc="mean",
        )
        .reset_index()
    )
    pivot["Country_Year_Average"] = pivot[["UPPER", "LOWER"]].mean(axis=1)
    world = pivot[pivot["Country"] == "World"].copy()
    world["Year"] = pd.to_datetime(world["Year"], format="%Y")
    return world.set_index("Year")["Country_Year_Average"]


def load_forecast() -> pd.DataFrame:
    forecast = pd.read_excel(DATA_DIR / "ARIMA_forecast_world.xlsx")
    forecast["Year"] = pd.to_datetime(forecast["Year"])
    return forecast


def main() -> None:
    history = load_world_history()
    forecast = load_forecast()
    ASSETS_DIR.mkdir(exist_ok=True)

    fig, ax = plt.subplots(figsize=(11, 6))
    ax.plot(history.index.year, history.values, linewidth=2, label="Historical biodiversity index")
    ax.plot(
        forecast["Year"].dt.year,
        forecast["Prediction"],
        linewidth=2,
        label="ARIMA forecast",
    )
    ax.axhline(0.50, linestyle="--", linewidth=1.5, label="0.50 threshold")

    crossing = forecast[forecast["Prediction"] <= 0.50].head(1)
    if not crossing.empty:
        year = int(crossing.iloc[0]["Year"].year)
        value = float(crossing.iloc[0]["Prediction"])
        ax.scatter([year], [value], zorder=3)
        ax.annotate(
            f"Threshold reached: {year}",
            xy=(year, value),
            xytext=(year - 45, value + 0.08),
            arrowprops={"arrowstyle": "->"},
        )

    ax.set_title("Global Biodiversity Index: Historical Trend and ARIMA Forecast")
    ax.set_xlabel("Year")
    ax.set_ylabel("Biodiversity index")
    ax.grid(alpha=0.25)
    ax.legend()
    fig.tight_layout()
    fig.savefig(ASSETS_DIR / "biodiversity-arima-forecast.png", dpi=180, bbox_inches="tight")
    plt.close(fig)


if __name__ == "__main__":
    main()
