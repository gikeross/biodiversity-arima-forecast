# Biodiversity Forecasting with ARIMA

A time-series analysis project exploring global biodiversity trends and forecasting when the biodiversity index could reach a critical level of **0.50**.

## Project Goal

Biodiversity is influenced by a complex combination of environmental pressures and human activity. This project combines biodiversity data with broader environmental indicators to explore long-term trends and build a forecast using an **ARIMA time-series model**.

The central analytical question is:

> Based on the historical trend, when could the global biodiversity index reach 0.50?

## Key Results

The original project analysis estimated that the modeled global biodiversity index could reach approximately **0.50 around 2132–2133** if the historical dynamics represented by the model continued.

The original notebook reported an out-of-sample ARIMA RMSE of approximately **0.001** for the selected configuration. The project also produced country-level estimates for 2100 using a separate linear-regression approach, providing a second perspective alongside the global time-series forecast.

These are long-horizon statistical projections rather than deterministic predictions. Policy interventions, changes in measurement, structural environmental shifts and unforeseen events could materially change the trajectory.

## Visual Analysis

The project includes an interactive Tableau dashboard that brings together the biodiversity analysis and broader environmental context. It is the quickest way to explore the visual side of the project:

[View the interactive Tableau dashboard](https://public.tableau.com/app/profile/giacomo.rossini/viz/PROJECT2_17025013200780/FINAL_dashboard?publish=yes)

The generated forecast data is also available in `data/ARIMA_forecast_world.xlsx`, while `data/bounded_predictions_2100.xlsx` contains the country-level 2100 estimates. These outputs make it possible to build additional charts or dashboards without rerunning the full exploratory notebook.

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

## Skills Demonstrated

- time-series forecasting with ARIMA
- model selection and RMSE evaluation
- residual diagnostics
- data cleaning and aggregation
- environmental-data analysis
- comparison of forecasting approaches
- reproducible file handling with `pathlib`
- data visualization with Tableau

## Limitations and Next Improvements

The forecast extrapolates historical statistical patterns far into the future, so uncertainty increases substantially with the forecast horizon. A stronger next version would add explicit prediction intervals to the published visuals, document the source/version of every dataset, restore or replace the missing Red List input, and export a static forecast chart into the repository so the headline result is visible directly on GitHub as well as in Tableau.
