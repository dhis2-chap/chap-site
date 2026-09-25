import mkdocs_gen_files
from pathlib import Path
import yaml
import requests

# input paths
cur_dir = Path(__file__).parent
model_catalog_path = cur_dir.parent / 'models' / 'model_catalog.yml'

# output dirs (mkdocs internal file system handling, relative paths) 
output_models_dir = Path('models/models')
output_index_path = output_models_dir / 'index.md'

MODEL_LIST_TEMPLATE = """
# Chap Model Catalogue

Explore our catalogue of user-contributed and published climate health models already made compatible with Chap. 
These can easily be added and run with the Chap modeling platform (instructions coming soon). 

!!! note "Want to see your own research model here?"

    [See our getting started guide](../../guides/contribute_model.md) for contributing your own climate health model into the Chap platform. 

---

<div class="grid cards" markdown>
{cards}
</div>
"""

MODEL_CARD_TEMPLATE = """
-   [{display_name}]({filename})
    <span class="status-chip status-{status_color}">{status_text}</span>

    {description}
"""

MODEL_PAGE_TEMPLATE = """
# {display_name}

> {description}

<img src="{organization_logo_url}">

---

## Overview
  
**Target:** `{target}`

**Supported Period Type:** `{supported_period_type}`

**Developed by:** {organization}

**Contact:** [{contact_email}](mailto:{contact_email})

**Source URL:** [{url}]({url})

!!! warning Deprecated

    {author_note}

---

## Covariates

**Required:**

{covariates_list}

**Allow Additional Covariates:** `{allow_free_additional_continuous_covariates}`

---

## User Options

{user_options}

---

## Runtime Environment

{runtime}


---
"""

def get_model_info(github_url, commit_or_branch):
    org,repo = github_url.split('/')[-2:]
    url = f'https://raw.githubusercontent.com/{org}/{repo}/{commit_or_branch.strip("@")}/MLproject'
    print(url)
    resp = requests.get(url)
    resp.raise_for_status()
    model_info = yaml.safe_load(resp.content)
    #print(model_info)
    model_info.update(model_info.get('meta_data', {})) # move metadata to toplevel
    return model_info

def generate_model_page_content(model_info):
    ## user options
    user_options = model_info.get('user_options', {})
    if user_options:
        for opt in user_options.values():
            if 'type' not in opt: opt['type'] = 'not supported yet...'
        model_info['user_options'] = '''
| Name | Type | Default | Description |
| --- | --- | --- | --- |
'''
        model_info['user_options'] += '\n'.join([
            '| {name} | {type} | {default} | ... |'.format(name=name, **user_option)
            for name,user_option in user_options.items()
        ])
    else:
        model_info['user_options'] = 'This model does not have configurable user options.'
    ## covariates
    model_info['covariates_list'] = '\n\n'.join([
        f'- {cov}' for cov in model_info['required_covariates']
    ])
    # misc
    model_info['runtime'] = f'**Docker:** `: {model_info["docker_env"]}`' if 'docker_env' in model_info else '**Python:** `: pyenv.yaml`'
    model_info['target'] = model_info.get('target', 'missing...')
    model_info['author_note'] = model_info.get('author_note', None)
    model_info['allow_free_additional_continuous_covariates'] = model_info.get('allow_free_additional_continuous_covariates', False)
    model_info['required_covariates'] = model_info.get('required_covariates', None)
    print(model_info)
    model_md = MODEL_PAGE_TEMPLATE.format(**model_info)
    print(model_md)
    return model_md

def generate_model_card_content(model_info):
    title = model_info['display_name']
    status_color = model_info['meta_data'].get('author_assessed_status', 'red')
    status_text = {
        'gray': 'Deprecated',
        'red': 'Experimental',
        'orange': 'Limited',
        'yellow': '...',
        'green': '...',
    }[status_color]
    card = MODEL_CARD_TEMPLATE.format(
        **model_info, 
        filename=f"{model_info['name']}.md",
        status_color=status_color,
        status_text=status_text,
    )
    return card

# read the model catalog entries
with open(model_catalog_path) as fobj:
    model_refs = yaml.safe_load(fobj)

# loop and all fetch model data
models = []
for model_ref in model_refs:
    print(model_ref)

    # get model info
    last_version = list(model_ref['versions'].values())[-1] # use last version only
    try:
        model_info = get_model_info(model_ref['url'], last_version)
        model_info.update(model_ref)
        models.append(model_info)
    except Exception as err:
        print(f'!!! Error getting model metadata, excluded from list of models: {err}')
        continue

# sort models by status
status_to_int = {
    'green': 0,
    'yellow': 1,
    'orange': 2,
    'red': 3,
    'gray': 4,
}
key = lambda info: status_to_int[
                        info['meta_data'].get('author_assessed_status', 'red')
                    ]
models = sorted(models, key=key)

# loop and process each model
cards = ""
for model_info in models:
    #print(model_info)
    
    # generate markdown content from model_info
    model_md = generate_model_page_content(model_info)

    # write to file
    model_md_path = output_models_dir / f"{model_info['name']}.md"
    with mkdocs_gen_files.open(model_md_path, 'w') as fobj:
        print('writing model page to path', model_md_path)
        fobj.write(model_md)

    # add link to model index
    card_md = generate_model_card_content(model_info)
    cards += card_md

# write model list index page
with mkdocs_gen_files.open(output_index_path, 'w') as f:
    print('writing index page to path', output_index_path)
    f.write(MODEL_LIST_TEMPLATE.format(cards=cards))
