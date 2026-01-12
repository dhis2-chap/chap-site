# 2. Fork a Minimalist Example

To get started with building your first CHAP-compatible model, you'll fork and clone a minimalist example repository. You can choose between Python or R based on your preferred programming language.

## Choose Your Language

We provide two minimalist example repositories demonstrating CHAP-compatible models:

| Language | Repository | Environment Manager |
|----------|-----------|---------------------|
| Python | [minimalist_example_uv](https://github.com/dhis2-chap/minimalist_example_uv) | uv |
| R | [minimalist_example_renv](https://github.com/dhis2-chap/minimalist_example_renv) | renv |

Both repositories implement the same simple linear regression model that predicts disease cases from rainfall and temperature. Choose the one matching your preferred language.

## Fork the Repository

1. Go to your chosen repository on GitHub:
   - **Python:** [github.com/dhis2-chap/minimalist_example_uv](https://github.com/dhis2-chap/minimalist_example_uv)
   - **R:** [github.com/dhis2-chap/minimalist_example_renv](https://github.com/dhis2-chap/minimalist_example_renv)

2. Click the **Fork** button in the top-right corner

3. Select your GitHub account as the destination

4. Keep the default settings and click **Create fork**

## Clone Your Fork

Clone the repository to your local machine. Replace `YOUR-USERNAME` with your GitHub username:

**Python:**
```bash
git clone https://github.com/YOUR-USERNAME/minimalist_example_uv.git
cd minimalist_example_uv
```

**R:**
```bash
git clone https://github.com/YOUR-USERNAME/minimalist_example_renv.git
cd minimalist_example_renv
```

## Repository Structure

Both repositories have a similar structure:

```
.
├── MLproject           # CHAP integration configuration
├── main.py / main.R    # Core training and prediction logic
├── isolated_run.py/R   # Script for testing without CHAP
├── input/              # Sample training and forecast data
└── output/             # Generated models and predictions
```

### Key Files

- **MLproject**: Defines how CHAP interacts with your model (entry points, parameters)
- **main.py / main.R**: Contains the `train` and `predict` functions
- **isolated_run**: Allows testing your model standalone, without CHAP

## Run the Model in Isolated Mode

Test that the model works before making changes:

**Python:**
```bash
uv run python isolated_run.py
```

**R:**
```bash
Rscript isolated_run.R
```

This runs the model on sample data and produces output in the `output/` directory.

## Exercise

### Fork and run the example

1. Fork one of the example repositories (Python or R)
2. Clone your fork to your local machine
3. Navigate to the repository directory
4. Run the model in isolated mode

**Verification:**
- You have a forked repository under your GitHub account
- Running `isolated_run` completes without errors
- The `output/` directory contains generated files

If all verifications passed, you're ready for the next guide: [Making Model Alterations](modify-model.md).
