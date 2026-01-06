# Setting Up Your Development Environment

This guide helps you install the tools needed to run CHAP models: **Docker** and either **uv** (Python) or **renv** (R).

---

## What Are Virtual Environments?

A **virtual environment** is an isolated space where your project's dependencies (packages and libraries) live separately from other projects. Without isolation, installing packages for one project can break another — for example, if Project A needs `pandas 1.5` but Project B needs `pandas 2.0`.

Virtual environments solve this by giving each project its own set of packages.

---

## Why These Tools?

| Tool       | What it isolates                    | When to use                                   |
| ---------- | ----------------------------------- | --------------------------------------------- |
| **uv**     | Python packages                     | Python projects, local development            |
| **renv**   | R packages                          | R projects, local development                 |
| **Docker** | Everything (OS, language, packages) | Sharing code, deployment, cross-platform work |

**uv** and **renv** isolate _packages_ — your project gets its own folder of dependencies.

**Docker** goes further — it isolates the _entire environment_ including the operating system. If code runs in a Docker container on your machine, it runs identically on any other machine. CHAP uses Docker to ensure models work the same everywhere.

You need **Docker** plus **one of** uv or renv (depending on whether you use Python or R).

---

## 1. Install Docker

**Official guide:** [docs.docker.com/get-docker](https://docs.docker.com/get-docker/)

<details markdown="1">
<summary><strong>macOS</strong></summary>

```bash
brew install --cask docker
```

Then open Docker from Applications.

Or download [Docker Desktop for Mac](https://www.docker.com/products/docker-desktop/) directly.

</details>

<details markdown="1">
<summary><strong>Windows</strong></summary>

Download [Docker Desktop for Windows](https://www.docker.com/products/docker-desktop/), run the installer, and restart if prompted.

</details>

<details markdown="1">
<summary><strong>Linux (Ubuntu/Debian)</strong></summary>

```bash
sudo apt-get update
sudo apt-get install docker.io
sudo systemctl start docker
sudo systemctl enable docker
sudo usermod -aG docker $USER
```

Then log out and log back in.

</details>

### Verify

```bash
docker --version
```

You should see something like `Docker version 29.0.0`.

---

## 2. Install uv (Python users)

**Official guide:** [docs.astral.sh/uv/getting-started/installation](https://docs.astral.sh/uv/getting-started/installation/)

<details markdown="1">
<summary><strong>macOS</strong></summary>

```bash
brew install uv
```

</details>

<details markdown="1">
<summary><strong>macOS / Linux / WSL (alternative)</strong></summary>

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
source $HOME/.local/bin/env
```

</details>

<details markdown="1">
<summary><strong>Windows (PowerShell)</strong></summary>

```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

</details>

### Verify

```bash
uv --version
```

You should see something like `uv 0.9.0`.

---

## 3. Install renv (R users)

**Official guide:** [rstudio.github.io/renv](https://rstudio.github.io/renv/)

### 1. Install R and RStudio

You need to have R installed to use renv. RStudio is a popular IDE for R, but is optional.

- Download and install R from the [CRAN website](https://cran.r-project.org/).
- (Optional) Download and install RStudio from the [RStudio website](https://posit.co/download/rstudio-desktop/).

### 2. Install renv

In R or RStudio, run:

```r
install.packages("renv")
```

### 3. Verify

```r
library(renv)
packageVersion("renv")
```

You should see a version number.

---

## Quick Reference

### uv (Python)

| Task                 | Command                   |
| -------------------- | ------------------------- |
| Install dependencies | `uv sync`                 |
| Add a package        | `uv add <package>`        |
| Run a script         | `uv run python script.py` |

### renv (R)

| Task                 | Command            |
| -------------------- | ------------------ |
| Restore dependencies | `renv::restore()`  |
| Save new packages    | `renv::snapshot()` |
| Check status         | `renv::status()`   |

### Docker

| Task                  | Command                    |
| --------------------- | -------------------------- |
| Run a container       | `docker run <image>`       |
| Build from Dockerfile | `docker build -t <name> .` |
| List containers       | `docker ps`                |

---

## Exercise

### 1. Test Docker

```bash
docker run hello-world
```

You should see "Hello from Docker!" and a message explaining what happened.

### 2. Test uv (Python) or renv (R)

<details markdown="1">
<summary><strong>Python</strong></summary>

```bash
git clone https://github.com/dhis2-chap/chap-workshop-python.git
cd chap-workshop-python
uv sync
uv run python --version
```

You should see packages installing, then a Python version number.

</details>

<details markdown="1">
<summary><strong>R</strong></summary>

```bash
git clone https://github.com/dhis2-chap/chap-workshop-r.git
cd chap-workshop-r
```

Then in R:

```r
renv::restore()
renv::status()
```

You should see packages installing, then "No issues found."

</details>

If these commands complete without errors, your environment is ready.
