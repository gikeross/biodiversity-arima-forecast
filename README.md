# Biodiversity Forecasting with ARIMA

A time-series analysis project exploring global biodiversity trends and forecasting when the biodiversity index could reach a critical level of **0.50**.

## Project Goal

Biodiversity is influenced by a complex combination of environmental pressures and human activity. This project combines biodiversity data with broader environmental indicators to explore long-term trends and build a forecast using an **ARIMA time-series model**.

The central analytical question is:

> Based on the historical trend, when could the global biodiversity index reach 0.50?

The ARIMA analysis produced an estimated crossing point between **2132 and 2133**.

## Analysis

The project investigates biodiversity alongside environmental indicators including:

- global temperature change
- CO2 emissions
- land and forest use
- resource consumption
- wildlife population trends

These variables provide environmental context around the biodiversity trend. They should be interpreted as related indicators rather than proof of direct causation.

## Forecasting Approach

### 1. Data preparation

Historical biodiversity data were cleaned and aggregated to create a usable time series. Country-level information was transformed where necessary and an average index was derived from available upper and lower values.

### 2. Train/test evaluation

The time series was split into training and testing data so that candidate ARIMA configurations could be evaluated out of sample.

### 3. ARIMA parameter selection

Different combinations of `p`, `d`, and `q` were evaluated, using RMSE to compare forecasting error. The selected configuration achieved an RMSE of approximately **0.001** in the project analysis.

### 4. Model diagnostics

Predicted and observed values were compared visually, and residual behaviour was inspected to assess model fit and the distribution of errors.

### 5. Long-term forecast

The fitted ARIMA model was extended from 2022 onward to estimate when the biodiversity index could reach 0.50.

### 6. Alternative model

A linear-regression forecast was also used as a comparison. For the year 2100, this approach produced a biodiversity index of approximately **0.44**, compared with approximately **0.54** from the ARIMA analysis, illustrating how strongly long-range results depend on modelling assumptions.

## Data Sources

The analysis uses environmental and biodiversity datasets from:

- Our World in Data
- GBIF
- European biodiversity data sources

## Key Files

| File | Purpose |
| --- | --- |
| `ARIMA_forecast_world.xlsx` | Historical biodiversity series and ARIMA forecast |
| `LAND_USED.xlsx` | Country-level land and forest-area analysis |
| `aggregate_exstintion_measure.xlsx` | Biodiversity index data |
| `avg_cou_biod_2021_RLI.xlsx` | Processed average biodiversity index |
| `annual_temp_and-co2-emissions-per-country.xlsx` | Temperature and CO2 data |
| `bounded_predictions_2100.xlsx` | Alternative linear-regression forecast |
| `eart_consumption_country.xlsx` | Country-level resource-consumption indicator |
| `global-living-planet-index.xlsx` | Wildlife population trend data |

## Key Result

The ARIMA forecast estimates that the biodiversity index could reach the critical value of **0.50 around 2132–2133** if the historical time-series dynamics represented in the model were to continue.

This is a long-horizon statistical projection rather than a deterministic prediction. Structural environmental changes, policy interventions, measurement changes and unexpected events could substantially alter the future trajectory.

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
- data visualization with Tableau
