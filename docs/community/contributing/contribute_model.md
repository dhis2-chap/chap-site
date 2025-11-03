# Share your model

Have you successfully published a scientific paper on climate health modelling and want to broaden the reach of your developed modelling approach? 

Or are you an epidemiologist or statistical modeler with basic skills in Python or R, and want to make it easy to run or share your own predictive model with others? 

If so, the Chap platform is here for you!

## Getting Started

1. Write your model code. You can start with our [minimalist example in R](https://github.com/dhis2-chap/minimalist_example_r/tree/main) or [Python](https://github.com/dhis2-chap/minimalist_example). You model code only needs to:

    * Read a CSV
    * Output predictions

2. Make your model Chap-compatible. All you need to do is create a file called `MLproject` where you: 

    * Describe your model metadata
    * Specify the runtime environment
    * Define the entry points for training and prediction

3. Chap takes care of the rest — validation, tuning, plots, and more.

For the full set of instructions, follow [our detailed technical guide](https://dhis2-chap.github.io/chap-core/external_models/developing_custom_models.html)

## Benefits

- Your model will be listed in our [publicly available model catalog](../models/models/index.md), with link to your codebase, as well as to your scientific article serving as a description of the model and its capabilities
- Your model will be available to run by anyone having installed Chap, including the many countries that have already set up connections to Chap from their national DHIS2 health information system. Countries can in this way rigorously evaluate the behavior of your model on their own data and may contact you if they have further questions or are considering to use it in operation.

## Requirements

- You have a climate health model published in a peer-reviewed journal or conference that includes a DOI for your publication.
- This papers describes a climate-informed model of health or agricultural outcomes that is available as open source codebase in a github repository.
- The model codebase is publicly available on GitHub and has been made compatible with Chap as described above.
