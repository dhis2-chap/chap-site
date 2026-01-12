# 1. Installing CHAP

## Why CHAP?

CHAP (Climate and Health Assessment Platform) is a tool for developing and evaluating disease prediction models that use climate data. The `chap` command-line tool allows you to:

- Evaluate models on historical data
- Compare model performance
- Test your models before integrating them with DHIS2

## Prerequisites

You should have `uv` installed from [Session 2](../session-2/virtual-environments.md). If not, install it first:

**Linux/macOS:**
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

**Windows (PowerShell):**
```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

## Installing CHAP

Install CHAP as a global tool using uv:

```bash
uv tool install chap-core
```

This installs the `chap` command-line tool globally, making it available from any directory.

To install a specific version (e.g., v1.0.1):

```bash
uv tool install chap-core==1.0.1
```

## Exercise

### Verify your installation

Run the following command:

```bash
chap --help
```

You should see output listing available commands including `evaluate2`, `plot-backtest`, and `export-metrics`.

**Verification:** If you see the help output with available commands, CHAP is installed correctly. You're ready for the next guide: [Fork a Minimalist Example](fork-example.md).
