# 4. Run Your Model Through CHAP

Until now, you have been running your model outside chap using Rscript or Python commands. We will now look into how you can run your model through CHAP. This gives you some benefits:

    - You can easily run your model against standard evaluation datasets
    - You can share your model with others in a standard way
    - You can make your model acessible through the Modeling app

In order to make your model run through chap, you will need the MLproject file that specifies how chap can run your model. You will also need to make sure that your model dependencies are specified in a way that chap can install them. In the minimalist repository you started out from, there should be an `MLproject` file already. If you are working with Python, you should also have a `pyproject.toml` file that specifies your dependencies using the `uv` format. If you are working with R, you should have an `renv.lock` file that specifies your R package dependencies.

## The MLproject File

The `MLproject` file defines how CHAP interacts with your model. It specifies:

- **name**: Model identifier
- **environment**: Points to your dependency file (`uv_env` for Python, `renv_env` for R)
- **entry_points**: The `train` and `predict` commands with their parameters

### Python Example (uv)

```yaml
name: minimalist_example_uv

uv_env: pyproject.toml

entry_points:
  train:
    parameters:
      train_data: str
      model: str
    command: "python main.py train {train_data} {model}"
  predict:
    parameters:
      historic_data: str
      future_data: str
      model: str
      out_file: str
    command: "python main.py predict {model} {historic_data} {future_data} {out_file}"
```

For Python models, the `uv_env` field points to `pyproject.toml`, which defines your dependencies:

```toml
[project]
name = "minimalist_example_uv"
version = "0.1.0"
requires-python = ">=3.10"
dependencies = [
    "pandas",
    "scikit-learn",
    "joblib",
    "cyclopts",
]
```

### R Example (renv)

```yaml
name: temp_r_model

renv_env: renv.lock

entry_points:
  train:
    parameters:
      train_data: str
      model: str
    command: "Rscript main.R train --train_data {train_data} --model {model}"
  predict:
    parameters:
      historic_data: str
      future_data: str
      model: str
      out_file: str
    command: "Rscript main.R predict --model {model} --historic_data {historic_data} --future_data {future_data} --out_file {out_file}"
```

For R models, the `renv_env` field points to `renv.lock`, which captures your R package dependencies.

As long as you don't need dependencies that are not already specified in the minimalist example you cloned, the MLProject file you alread have should work and you can simply continue to the next section, which is how to run evaluations using chap.

## Running Evaluations

Use the `chap evaluate` command to run your model against a dataset:

```bash
chap evaluate --model-name /path/to/your/model --dataset-name ISIMIP_dengue_harmonized --dataset-country brazil --report-filename report.pdf
```

**Parameters:**

- `--model-name`: Path to your local model directory (where MLproject is located)
- `--dataset-name`: The evaluation dataset to use
- `--dataset-country`: Country filter for the dataset
- `--report-filename`: Output PDF report

## Exercise

1. Navigate to your forked model directory
2. Make sure the MLproject file is present and correct according to the dependencies you need.
2. Run `chap evaluate` with your model path
3. Check the generated report.pdf

**Verification:**

- The command completes without errors
- A report.pdf file is generated
