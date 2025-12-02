# Public landing page for the Chap Modeling Platform

This repository contains the public landing page for the Chap Modeling Platform. 

The website is written in [Markdown format](https://www.markdownguide.org/cheat-sheet/), which is then automatically converted to HTML and served with Python and [Material for MkDocs](https://squidfunk.github.io/mkdocs-material/). 

Any changes to the main branch is automatically deployed to the live site.

## Overview

- `mkdocs.yml`: Defines the website theme, page menu structure, and other configurations. 
- `docs/`: Contains the website pages written in Markdown format. 
- `docs/assets/`: Contains static images and custom CSS. 

## Local testing

1. Clone or download the github repository to your computer.
2. Install the required packages for local development.

        >>> pip install -r requirements.txt

3. Run the local development server. 

        >>> mkdocs serve

    Note that changes to any of the source documents will trigger a server rebuild and update the local development server. 

4. Visit the local development server at localhost:8000. 

## Contributions

For minor changes, push your local changes directly back to the main branch. 

For major changes, create a new branch and submit a Pull Request to the main branch, and ping maintainers for code review. 

All pushes to the main branch will trigger Github Actions that builds and updates the site at https://chap.dhis2.org. 
