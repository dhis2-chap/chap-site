# Getting started as a model developer

The Chap platform brings several advantages to you as a model developer:

- It provides a [broad range of supporting functionality for modelling](https://chap.dhis2.org/chap-modeling-platform/external_models/supporting_functionality/index.md), allowing you to focus on what is unique in your project, while relying on Chap for data parsing, model tuning, rigorous model assessment and more.
- It allows you to evaluate your model [side-by-side with a range of other models](https://chap.dhis2.org/chap-modeling-platform/external_models/side_by_side_comparison/index.md) in the field
- It comes with [native connection to DHIS2 and the DHIS2 Modelling App](https://chap.dhis2.org/chap-modeling-platform/external_models/chap-dhis2-connection/index.md), and includes mechanisms to disseminate your model to a large number of health ministries that use DHIS2 as their national health information system.

## How a model runs in Chap

A Chap model is a train script and a predict script, in R or Python, plus a short `MLproject` file that tells Chap how to run them. Once your model is Chap-compatible, you can use it in two ways:

- **On your own machine**, with the `chap` command-line tool. One command evaluates the model on a dataset and plots its forecasts:

  ```console
  chap eval --model-name . --dataset-csv data.csv --output-file eval.nc --plot --run-config.as-chapkit
  ```

- **In the Chap Modeling App**, where users can evaluate it on DHIS2 data, compare it with other models and make forecasts. For this, you package the model as a Docker image and add it to a Chap installation, see [Running Your Own Model](https://chap.dhis2.org/chap-modeling-platform/modeling-app/running-your-own-model/index.md).

## Where to start

First [set up your machine](https://chap.dhis2.org/chap-modeling-platform/external_models/setup/index.md). Then pick the guide that fits you:

| You...                                                                | Start here                                                                                                                         |
| --------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------- |
| already have a forecasting model in R or Python                       | [Bring your existing model to Chap](https://chap.dhis2.org/chap-modeling-platform/external_models/existing_model/index.md)         |
| want to build a new model                                             | [Build a new model from a template](https://chap.dhis2.org/chap-modeling-platform/external_models/mlproject_tutorial/index.md)     |
| are not used to the terminal, git, or installing Python or R packages | [Development tools](https://chap.dhis2.org/chap-modeling-platform/external_models/development_tools/index.md), then come back here |
| want to learn statistical modelling and forecasting                   | [Learning modelling](https://chap.dhis2.org/chap-modeling-platform/external_models/learn_modelling/index.md)                       |

Both model guides use the same `MLproject` format and the same `chap eval` command. They only differ in where you start: from your own code, or from a template.

Strictly, Chap only requires that a model exposes the chapkit REST API. The train and predict scripts and the `MLproject` file are the recommended way to get there, since chapkit then provides the API for you. Advanced users can write a service that implements the API directly, see the [chapkit documentation](https://dhis2-chap.github.io/chapkit/). Most models do not need this.
