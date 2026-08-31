from pathlib import Path
from math import sqrt

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error
from statsmodels.tsa.arima.model import ARIMA

ROOT_DIR = Path(__file__).resolve().parent
DATA_DIR = ROOT_DIR / "data"
ASSETS_DIR = ROOT_DIR / "assets"
BIODIVERSITY_FILE = DATA_DIR / "aggregate_exstintion_measure.xlsx"
FORECAST_CHART = ASSETS_DIR / "biodiversity-arima-forecast.png"


def load_biodiversity_data() -> pd.DataFrame:
    """Load the biodiversity dataset using a repository-relative path."""
    if not BIODIVERSITY_FILE.exists():
        raise FileNotFoundError(
            f"Missing dataset: {BIODIVERSITY_FILE}. "
            "Place aggregate_exstintion_measure.xlsx in the data directory."
        )
    return pd.read_excel(BIODIVERSITY_FILE)


def prepare_world_series(biodiv: pd.DataFrame) -> tuple[pd.DataFrame, pd.Series]:
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
    world = world.set_index("Year")
    return pivot, world["Country_Year_Average"]


def evaluate_arima_model(values: np.ndarray, order: tuple[int, int, int]) -> float:
    train_size = int(len(values) * 0.66)
    train, test = values[:train_size], values[train_size:]
    history = list(train)
    predictions = []

    for actual in test:
        model = ARIMA(history, order=order).fit()
        predictions.append(model.forecast()[0])
        history.append(actual)

    return sqrt(mean_squared_error(test, predictions))


def select_arima_order(series: pd.Series) -> tuple[tuple[int, int, int], float]:
    values = series.astype("float32").values
    best_order = None
    best_rmse = float("inf")

    for p in [0, 1, 2, 4, 6, 8, 10]:
        for d in range(3):
            for q in range(3):
                order = (p, d, q)
                try:
                    rmse = evaluate_arima_model(values, order)
                except Exception:
                    continue
                if rmse < best_rmse:
                    best_order, best_rmse = order, rmse

    if best_order is None:
        raise RuntimeError("No ARIMA configuration could be fitted successfully.")
    return best_order, best_rmse


def forecast_world(series: pd.Series, order=(4, 1, 0), end_year=2200) -> pd.DataFrame:
    model = ARIMA(series, order=order).fit()
    start_year = int(series.index.max().year) + 1
    years = pd.date_range(
        f"{start_year}-01-01", f"{end_year}-01-01", freq="YS"
    )
    forecast = model.forecast(len(years))
    return pd.DataFrame(
        {"Year": years, "COU": "World", "Prediction": np.asarray(forecast)}
    )


def forecast_countries_2100(pivot: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for country, country_data in pivot.groupby("Country"):
        clean = country_data.dropna(subset=["Year", "Country_Year_Average"])
        if len(clean) < 2:
            continue
        model = LinearRegression().fit(
            clean[["Year"]].values, clean["Country_Year_Average"].values
        )
        prediction = float(model.predict(np.array([[2100]]))[0])
        rows.append(
            {
                "Country": country,
                "2100_Bounded_Prediction": min(max(prediction, 0.0), 1.0),
            }
        )
    return pd.DataFrame(rows)


def save_forecast_chart(series: pd.Series, forecast: pd.DataFrame) -> None:
    """Save a recruiter-friendly static chart from the historical and forecast data."""
    ASSETS_DIR.mkdir(exist_ok=True)

    fig, ax = plt.subplots(figsize=(11, 6))
    ax.plot(series.index.year, series.values, linewidth=2, label="Historical biodiversity index")
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
    fig.savefig(FORECAST_CHART, dpi=180, bbox_inches="tight")
    plt.close(fig)


def main() -> None:
    biodiv = load_biodiversity_data()
    pivot, world_series = prepare_world_series(biodiv)

    best_order, best_rmse = select_arima_order(world_series)
    print(f"Best ARIMA order: {best_order}; RMSE: {best_rmse:.4f}")

    world_forecast = forecast_world(world_series, order=best_order)
    country_forecast = forecast_countries_2100(pivot)

    world_forecast.to_excel(DATA_DIR / "ARIMA_forecast_world.xlsx", index=False)
    country_forecast.to_excel(DATA_DIR / "bounded_predictions_2100.xlsx", index=False)
    save_forecast_chart(world_series, world_forecast)

    crossing = world_forecast[world_forecast["Prediction"] <= 0.50].head(1)
    if not crossing.empty:
        year = crossing.iloc[0]["Year"].year
        value = crossing.iloc[0]["Prediction"]
        print(f"Forecast first reaches 0.50 or below in {year} ({value:.4f}).")

    print(f"Saved forecast chart to {FORECAST_CHART.relative_to(ROOT_DIR)}")


if __name__ == "__main__":
    main()
