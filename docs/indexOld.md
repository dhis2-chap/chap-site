# Chap - The Climate & Health Modeling Platform

## Our Goal: To be the central platform for climate health modeling in the world

Chap is a Climate & Health Modeling Platform that brings together climate health models into a unified ecosystem, connecting researchers and cutting-edge epidimiological models to policy makers and health practitioners. It makes complex modeling workflows accessible, automates rigorous validation, and integrates directly with DHIS2, the world's leading health information system.

[Get Started for Modelers](guides/contribute_model.md){ .md-button .md-button--primary }
[Get Started for Developers](https://dhis2-chap.github.io/chap-core/){ .md-button .md-button--primary }
[Connect with the Community](https://community.dhis2.org/t/about-the-chap-modeling-category/61403){ .md-button .md-button--primary }

Check out this presentation on Chap and the Modeling App, from the DHIS2 Annual Conference 2025:

![type:video](https://www.youtube.com/embed/aa1EfSuCUQ0?si=CdYA-ZtkooX3lfUC)

## Key Resources

The Chap modeling platform builds on and integrates with several resources and applications that supports its use. 

<div class="grid cards" markdown>

-   Chap Core

    ```bash
    chap evaluate --model-name https://github.com/dhis2-chap/chap_auto_ewars --dataset-name ISIMIP_dengue_harmonized --dataset-country brazil
    ```

    Chap Core is the core processing engine written in Python that handles model orchestration, data pipelines, validation, metrics, and hyperparameter tuning. Chap Core supports streamlined integration with the DHIS2 system for accessing health data and disseminating forecasts, but is also fully functional as a stand-alone Python package and commandline tool.

    [View on Github](https://github.com/dhis2-chap/chap-core){ .md-button .md-button--primary } 

-   Modeling App

    ![Modeling App](assets/images/modeling-app.png){.tool-card-photo}

    The Modeling App allows users to run models directly within DHIS2. It provides a UI interface for configuring inputs and visualizing predictions at national and subnational levels.

    [View on Github](https://github.com/dhis2-chap/chap-frontend-monorepo){ .md-button .md-button--primary }

-   Climate App

    ![Climate App](assets/images/climate-app.png){.tool-card-photo}

    The climate app integrates and harmonizes gridded climate data (e.g., rainfall, temperature) into DHIS2-compatible formats, supporting the need for climate and environmental covariates in the Chap modeling platform.

    [View on Github](https://github.com/dhis2-chap/climate-app){ .md-button .md-button--primary } 

</div>

## Please join us!

We strive to make all parts of the project development open and transparent, so as to make it as easy as possible to join the Chap community.

If you are interested in joining this effort, there are several options:

- If you have developed and published a climate and health model, we offer to [help disseminate your model](guides/contribute_model.md) and publication on our website and network. 
- If you mainly want to get updates and news about what is happening, please join our [Chap email list](https://sympa.uio.no/hisp.uio.no/subscribe/chap-updates)
- If you want to contribute with code development or model development, a good place to start is the [chap-core github repository](https://github.com/dhis2-chap/chap-core). Please [read the documentation](https://dhis2-chap.github.io/chap-core/) before reaching out to us with questions, and feel free to look into any of the [open Github issues](https://github.com/orgs/dhis2-chap/projects/4/views/3). We are happy to take code contributions related to these. Use the Github issues system for inquiries. 
- For developers interested in front-end development, the [chap monorepo repository](https://github.com/dhis2-chap/chap-frontend-monorepo) might be more relevant as a starting-point.
- For any other inquiries, please [send us an email](mailto:chap@dhis2.org), or consult the multitude of open resources connected to the project below.
