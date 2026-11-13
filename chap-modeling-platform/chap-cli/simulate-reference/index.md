# simulate Command Reference

The `simulate` command runs a model's optional `simulate` entry point to generate disease data for the locations and periods in a covariate CSV.

## Synopsis

```console
chap simulate <MODEL_NAME> <DATASET_CSV> <OUT_FILE> [OPTIONS]
```

## Description

`chap simulate`:

1. Loads the model template from a local MLProject directory or a GitHub URL.
1. Loads covariates from a CSV file (auto-discovering the matching `.geojson` if present). The CSV does not need a `disease_cases` column; rows that have one are kept as observed history.
1. Invokes the MLProject's `simulate` entry point.
1. Checks that the output covers the same locations and periods, has the target for every row, and keeps the observed values unchanged.
1. Writes the result to `out_file`, plus a `.geojson` next to it if the input had polygons.

Each parameter can also be passed as a keyword flag (`--model-name`, `--dataset-csv`, `--out-file`). The output is a regular Chap dataset and can be used with `chap eval`. See [Additional Configuration → Simulate Entry Point](https://chap.dhis2.org/chap-modeling-platform/external_models/additional_configuration/#simulate-entry-point) for how to define the entry point.

## Options

| Parameter                         | Description                                                               | Default |
| --------------------------------- | ------------------------------------------------------------------------- | ------- |
| `--model-configuration-yaml`      | YAML file with `user_option_values`, e.g. simulation parameters or a seed | None    |
| `--run-config.ignore-environment` | Skip automatic environment setup                                          | false   |
| `--run-config.debug`              | Enable verbose debug logging                                              | false   |

## Example

```console
chap simulate \
    --model-name https://github.com/chap-models/climate_simulation_model \
    --dataset-csv ./covariates.csv \
    --out-file ./simulated.csv
```

To continue a simulation, append the new periods' covariates to the previous output (leaving `disease_cases` empty for them) and run the command again on that file. Only the new periods are simulated.
