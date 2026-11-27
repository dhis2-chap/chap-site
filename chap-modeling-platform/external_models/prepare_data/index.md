# Chap data format

## 1) Chap data format

Chap models are designed to be interchangeable: any model that follows the Chap interface can be evaluated on any Chap-compatible dataset. For this to work, datasets must follow a common **CSV format** so that models know which columns to expect and how to parse time periods and locations.

The required columns in the CSV-file are:

| Column          | Description                                                      |
| --------------- | ---------------------------------------------------------------- |
| `time_period`   | Time period in `YYYY-MM` (monthly) or `YYYY-Wnn` (weekly) format |
| `location`      | Location identifier matching the GeoJSON features                |
| `disease_cases` | Observed case counts                                             |

Additional columns (e.g. `rainfall`, `mean_temperature`, `population`) are used as covariates by models that need them. A matching GeoJSON file with region polygons is optional but recommended for spatial visualizations.

## 2) Getting data

Choose the approach that fits your situation:

- [Option 1: Use your own data](https://chap.dhis2.org/chap-modeling-platform/external_models/prepare_data/own-data/index.md) — convert an existing dataset to the Chap format
- [Option 2: Use DHIS2 data](https://chap.dhis2.org/chap-modeling-platform/external_models/prepare_data/dhis2-data/index.md) — export data from a DHIS2 instance
- [Option 3: Use example data](https://chap.dhis2.org/chap-modeling-platform/external_models/prepare_data/example-data/index.md) — download a ready-made dataset to get started quickly
