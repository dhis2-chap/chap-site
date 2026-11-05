# Using the CLI Tool

The Chap CLI provides commands for evaluating disease prediction models, visualizing results, and exporting metrics.

## Quick Start

The main workflow consists of three commands:

1. **`chap eval`** - Run a backtest and export results to NetCDF format
1. **`chap plot-backtest`** - Generate visualizations from evaluation results
1. **`chap export-metrics`** - Export and compare metrics across evaluations

See the [Evaluation Workflow](https://chap.dhis2.org/chap-modeling-platform/chap-cli/evaluation-workflow/index.md) guide for detailed usage and examples.

To set up a model and dataset once and then run `chap eval` without options, create a [Chap project](https://chap.dhis2.org/chap-modeling-platform/chap-cli/projects/index.md) with `chap init`.

## Documentation

- [Setup](https://chap.dhis2.org/chap-modeling-platform/chap-cli/chap-core-cli-setup/index.md) - How to install and configure the CLI
- [Evaluation Workflow](https://chap.dhis2.org/chap-modeling-platform/chap-cli/evaluation-workflow/index.md) - Complete guide to evaluating and comparing models
- [Chap Projects](https://chap.dhis2.org/chap-modeling-platform/chap-cli/projects/index.md) - Keep a model, dataset and settings in a directory and run `chap eval` without options

## Command Reference

- [eval](https://chap.dhis2.org/chap-modeling-platform/chap-cli/eval-reference/index.md) - Full reference for the eval command with all parameters
- [report](https://chap.dhis2.org/chap-modeling-platform/chap-cli/report-reference/index.md) - Generate a PDF report from a trained model
- [explain-lime](https://chap.dhis2.org/chap-modeling-platform/chap-cli/explain-lime-reference/index.md) - Generate a LIME importance weighting for a single prediction
- [simulate](https://chap.dhis2.org/chap-modeling-platform/chap-cli/simulate-reference/index.md) - Generate a synthetic dataset from a simulation model
- [sanity-check-model](https://chap.dhis2.org/chap-modeling-platform/chap-cli/sanity-check-model-reference/index.md) - Check quickly that a model can be trained and make forecasts
- [plot-dataset](https://chap.dhis2.org/chap-modeling-platform/chap-cli/plot-dataset-reference/index.md) - Plot a dataset's columns over time, in a browser or to a file
