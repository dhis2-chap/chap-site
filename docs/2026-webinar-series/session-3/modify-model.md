# 3. Making Model Alterations

## Understanding the Model

The minimalist example implements a simple linear regression that predicts disease cases from climate variables (rainfall and temperature). While not intended to be accurate, it demonstrates the structure CHAP expects.

### The Main File

Open `main.py` (Python) or `main.R` (R) to see the core logic:

**Key functions:**

- **train**: Reads training data, fits a model, and saves it to the output directory
- **predict**: Loads the trained model and generates predictions from climate forecast data

### The MLproject File

The `MLproject` file tells CHAP how to run your model:

```yaml
name: minimalist_example

entry_points:
  train:
    command: "python main.py train"
  predict:
    command: "python main.py predict"
```

## Simple Modifications

Here are some modifications you can try:

### 1. Change the Model Type

**Python (main.py):** Replace LinearRegression with a different sklearn model:

```python
# Original
from sklearn.linear_model import LinearRegression
reg = LinearRegression()

# Try Ridge regression instead
from sklearn.linear_model import Ridge
reg = Ridge(alpha=1.0)
```

**R (main.R):** Try a different model formula or method.

### 2. Add or Remove Features

Modify which columns are used as input features:

**Python:**
```python
# Original uses rainfall and mean_temperature
X = df[["rainfall", "mean_temperature"]]

# Try using only rainfall
X = df[["rainfall"]]
```

### 3. Add Data Preprocessing

Add simple preprocessing steps like scaling:

**Python:**
```python
from sklearn.preprocessing import StandardScaler

scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)
```

## Test Your Changes

After making changes, run the isolated test to verify everything works:

**Python:**
```bash
uv run python isolated_run.py
```

**R:**
```bash
Rscript isolated_run.R
```

Check that:
- The script runs without errors
- Output files are generated in the `output/` directory

## Commit and Push Your Changes

Once your modifications work, save them to your fork:

```bash
git add .
git commit -m "Modified model: [describe your change]"
git push origin main
```

## Exercise

### Make a modification

1. Open `main.py` or `main.R` in your editor
2. Make one simple modification (e.g., change the model type or features)
3. Run `isolated_run` to verify your changes work
4. Commit and push your changes to your fork

**Verification:**
- Your modified code runs without errors
- Output is generated in the `output/` directory
- Your changes are pushed to your GitHub fork

Congratulations! You've made your first modifications to a CHAP-compatible model.
