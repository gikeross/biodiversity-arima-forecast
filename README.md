# Biodiversity Forecasting with ARIMA

A time-series analysis project exploring global biodiversity trends and forecasting when the biodiversity index could reach a critical level of **0.50**.

## Project Goal

Biodiversity is influenced by a complex combination of environmental pressures and human activity. This project combines biodiversity data with broader environmental indicators to explore long-term trends and build a forecast using an **ARIMA time-series model**.

The central analytical question is:

> Based on the historical trend, when could the global biodiversity index reach 0.50?

The original project analysis estimated a crossing point around **2132–2133**.

## Portable Analysis

`analysis.py` is the recommended entry point for running the core forecasting workflow. It replaces the original machine-specific `/Users/...` paths with repository-relative paths under `data/` and writes generated forecast files back into that folder.

Install the dependencies:

```bash
pip install -r requirements.txt
```

Then run:

```bash
python analysis.py
```

The historical Jupyter notebook, `prev_biodivers.ipynb`, is kept as the original exploratory analysis and presentation of the work.

## Forecasting Approach

The project:

1. cleans and aggregates historical biodiversity data;
2. creates a global biodiversity time series;
3. evaluates candidate ARIMA `(p, d, q)` configurations using out-of-sample RMSE;
4. fits the selected ARIMA model and extends the forecast to 2200;
5. compares the time-series forecast with country-level linear-regression estimates for 2100.

The original notebook reported an ARIMA RMSE of approximately **0.001** for the selected configuration.

## Data

Project datasets are stored in `data/`. Key files include:

| File | Purpose |
| --- | --- |
| `data/aggregate_exstintion_measure.xlsx` | Main biodiversity index input |
| `data/ARIMA_forecast_world.xlsx` | Generated global ARIMA forecast |
| `data/bounded_predictions_2100.xlsx` | Country-level linear-regression forecast |
| `data/LAND_USED.xlsx` | Land and forest-use analysis |
| `data/annual_temp_and-co2-emissions-per-country.xlsx` | Temperature and CO2 data |
| `data/global-living-planet-index.xlsx` | Wildlife population trend data |
| `data/eart_consumption_country.xlsx` | Resource-consumption indicator |

The historical notebook also references `red-list-index.xlsx`. That source file is **not currently included in the repository**, so the related optional merge step is not part of the portable `analysis.py` workflow.

## Data Sources

The analysis uses environmental and biodiversity datasets from sources including:

- Our World in Data
- GBIF
- European biodiversity data sources

## Key Result

The project forecast suggests that the biodiversity index could reach approximately **0.50 around 2132–2133** if the historical time-series dynamics represented by the model continued.

This is a long-horizon statistical projection, not a deterministic prediction. Policy interventions, measurement changes, structural environmental shifts and unforeseen events could materially change the trajectory.

## Visualization

The project also includes an interactive Tableau dashboard presenting the analysis and environmental context.

[View the Tableau dashboard](https://public.tableau.com/app/profile/giacomo.rossini/viz/PROJECT2_17025013200780/FINAL_dashboard?publish=yes)

## Skills Demonstrated

- time-series forecasting with ARIMA
- model selection and RMSE evaluation
- residual diagnostics
- data cleaning and aggregation
- environmental-data analysis
- comparison of forecasting approaches
- reproducible file handling with `pathlib`
- data visualization with Tableau
