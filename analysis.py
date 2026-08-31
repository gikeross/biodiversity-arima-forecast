"""Portable biodiversity forecasting workflow with validation and uncertainty."""

from pathlib import Path
from math import sqrt

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, mean_squared_error
from statsmodels.tsa.arima.model import ARIMA

ROOT_DIR = Path(__file__).resolve().parent
DATA_DIR = ROOT_DIR / "data"
ASSETS_DIR = ROOT_DIR / "assets"
RESULTS_DIR = ROOT_DIR / "results"
BIODIVERSITY_FILE = DATA_DIR / "aggregate_exstintion_measure.xlsx"
FORECAST_CHART = ASSETS_DIR / "biodiversity-arima-forecast.png"
RESULTS_FILE = RESULTS_DIR / "model_results.csv"


def load_biodiversity_data() -> pd.DataFrame:
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
    world = world.set_index("Year").sort_index()
    return pivot, world["Country_Year_Average"].dropna()


def rolling_origin_scores(
    series: pd.Series,
    order: tuple[int, int, int],
    initial_fraction: float = 0.66,
) -> dict[str, float]:
    """Evaluate one-step-ahead ARIMA forecasts with expanding-window validation."""
    values = series.astype(float).values
    initial_size = max(5, int(len(values) * initial_fraction))
    actuals, predictions, naive_predictions = [], [], []

    for i in range(initial_size, len(values)):
        history = values[:i]
        actual = values[i]

        model = ARIMA(history, order=order).fit()
        prediction = float(model.forecast(1)[0])
        naive_prediction = float(history[-1])

        actuals.append(actual)
        predictions.append(prediction)
        naive_predictions.append(naive_prediction)

    return {
        "arima_rmse": sqrt(mean_squared_error(actuals, predictions)),
        "arima_mae": mean_absolute_error(actuals, predictions),
        "naive_rmse": sqrt(mean_squared_error(actuals, naive_predictions)),
        "naive_mae": mean_absolute_error(actuals, naive_predictions),
    }


def select_arima_order(series: pd.Series) -> tuple[tuple[int, int, int], dict[str, float]]:
    best_order = None
    best_scores = None

    for p in [0, 1, 2, 4, 6, 8, 10]:
        for d in range(3):
            for q in range(3):
                order = (p, d, q)
                try:
                    scores = rolling_origin_scores(series, order)
                except Exception:
                    continue
                if best_scores is None or scores["arima_rmse"] < best_scores["arima_rmse"]:
                    best_order, best_scores = order, scores

    if best_order is None or best_scores is None:
        raise RuntimeError("No ARIMA configuration could be fitted successfully.")
    return best_order, best_scores


def forecast_world(
    series: pd.Series,
    order: tuple[int, int, int],
    end_year: int = 2200,
) -> pd.DataFrame:
    """Forecast with 80% and 95% prediction intervals."""
    model = ARIMA(series, order=order).fit()
    start_year = int(series.index.max().year) + 1
    years = pd.date_range(f"{start_year}-01-01", f"{end_year}-01-01", freq="YS")
    forecast_res = model.get_forecast(steps=len(years))
    mean = np.asarray(forecast_res.predicted_mean)

    ci95 = forecast_res.conf_int(alpha=0.05)
    ci80 = forecast_res.conf_int(alpha=0.20)

    return pd.DataFrame(
        {
            "Year": years,
            "COU": "World",
            "Prediction": mean,
            "Lower_80": np.asarray(ci80.iloc[:, 0]),
            "Upper_80": np.asarray(ci80.iloc[:, 1]),
            "Lower_95": np.asarray(ci95.iloc[:, 0]),
            "Upper_95": np.asarray(ci95.iloc[:, 1]),
        }
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
    ASSETS_DIR.mkdir(exist_ok=True)

    fig, ax = plt.subplots(figsize=(11, 6))
    years = forecast["Year"].dt.year
    ax.plot(series.index.year, series.values, linewidth=2, label="Historical biodiversity index")
    ax.plot(years, forecast["Prediction"], linewidth=2, label="ARIMA forecast")
    ax.fill_between(years, forecast["Lower_95"], forecast["Upper_95"], alpha=0.15, label="95% interval")
    ax.fill_between(years, forecast["Lower_80"], forecast["Upper_80"], alpha=0.25, label="80% interval")
    ax.axhline(0.50, linestyle="--", linewidth=1.5, label="0.50 threshold")

    crossing = forecast[forecast["Prediction"] <= 0.50].head(1)
    if not crossing.empty:
        year = int(crossing.iloc[0]["Year"].year)
        value = float(crossing.iloc[0]["Prediction"])
        ax.scatter([year], [value], zorder=3)
        ax.annotate(
            f"Point forecast reaches 0.50: {year}",
            xy=(year, value),
            xytext=(year - 55, value + 0.08),
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


def save_results(order: tuple[int, int, int], scores: dict[str, float], forecast: pd.DataFrame) -> None:
    RESULTS_DIR.mkdir(exist_ok=True)
    crossing = forecast[forecast["Prediction"] <= 0.50].head(1)
    crossing_year = int(crossing.iloc[0]["Year"].year) if not crossing.empty else np.nan

    milestones = {}
    for year in [2050, 2100, 2150]:
        row = forecast[forecast["Year"].dt.year == year]
        milestones[f"forecast_{year}"] = float(row.iloc[0]["Prediction"]) if not row.empty else np.nan

    result_row = {
        "arima_order": str(order),
        **scores,
        "rmse_improvement_vs_naive_pct": 100 * (scores["naive_rmse"] - scores["arima_rmse"]) / scores["naive_rmse"],
        "threshold_crossing_year_point_forecast": crossing_year,
        **milestones,
    }
    pd.DataFrame([result_row]).to_csv(RESULTS_FILE, index=False)


def main() -> None:
    biodiv = load_biodiversity_data()
    pivot, world_series = prepare_world_series(biodiv)

    best_order, scores = select_arima_order(world_series)
    print(
        f"Best ARIMA order: {best_order}; "
        f"rolling RMSE: {scores['arima_rmse']:.4f}; "
        f"naive RMSE: {scores['naive_rmse']:.4f}"
    )

    world_forecast = forecast_world(world_series, order=best_order)
    country_forecast = forecast_countries_2100(pivot)

    world_forecast.to_excel(DATA_DIR / "ARIMA_forecast_world.xlsx", index=False)
    country_forecast.to_excel(DATA_DIR / "bounded_predictions_2100.xlsx", index=False)
    save_forecast_chart(world_series, world_forecast)
    save_results(best_order, scores, world_forecast)

    print(f"Saved forecast chart to {FORECAST_CHART.relative_to(ROOT_DIR)}")
    print(f"Saved validation summary to {RESULTS_FILE.relative_to(ROOT_DIR)}")


if __name__ == "__main__":
    main()
