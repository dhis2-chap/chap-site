# Configuring your model

Assuming you have followed the [guide to create your own Chap-compatible model](contribute_model.md), next you will have to tell Chap where to find your model. 

By default, the Chap Modeling Platform comes with a selection of builtin models as defined in `chap-core/config/configured_models/default.yml`. 

To add additional models, add a new file with a name of your choice, e.g. `chap-core/config/configured_models/extra.yml`. In that file, add one or more list entries for each configured model you want to add, for example: 

        - url: https://github.com/dhis2-chap/ewars_template
            versions:
                v1: "d666546c3975994183a6386468af217aba06b6c5"
                v2: 'main'
            configurations:
                default:
                    user_option_values:
                        n_lags: 3
                        precision: 1
                    additional_continuous_covariates:
                        - rainfall
                        - mean_temperature

## Model template URL

This is the url to your Chap-compatible model template repository on GitHub. 

## Versions

You can specify one or more versions of your model template as you make changes and improve your model, in order to not interupt the work of others who might be relying on an older version of your model. 

Each version key can be any name tag to identify your version, e.g. `v1`. The value is either the commit hash or branch name containing that specific version. 

## Configurations

Here you can specify one or more configurations of your model template, meaning that you can specify which parameters and user inputs are allowed for your model. Usually it's sufficient with a single model configuration. 

Each configuration key can be any name tag to identify your version, e.g. `default`. The values can be any of the following:

* `user_option_values`:

    A dict of key-value pairs specifying user option values. These must match the user option names and types as specified in the model template (`user_options`).

* `additional_continuous_variables`:

    A list of names for the additional continuous covariates, if your model template allows it (`allow_additional_continuous_covariates` is set to true).
