import mkdocs_gen_files
from pathlib import Path
import yaml
import requests

team_config_path = "docs/about/team.yml"
team_list_path = "about/team.md"

TEAM_LIST_TEMPLATE = """
# The Team

The Chap Modeling Platform is developed by a core team at the [HISP Oslo office](https://www.mn.uio.no/hisp/english/about/). 
Additional support is provided by members of the broader [HISP climate and health team](https://www.mn.uio.no/hisp/english/research/hisp-climate-and-health-team.html), 
as well as members from various country HISP offices. 
The core team includes, in alphabetical order: 

<div class="grid cards" markdown>
{cards}
</div>
"""

MEMBER_CARD_TEMPLATE = """
-   ![{name}]({photo}){{.team-member-photo}}

    {name}

    ---

    {roles}
"""

DEFAULT_PHOTO_URL = 'https://cdn-icons-png.flaticon.com/512/3686/3686930.png'

def generate_member_card_content(member_info):
    member_info['photo'] = member_info.get('photo', DEFAULT_PHOTO_URL)
    card = MEMBER_CARD_TEMPLATE.format(
        **member_info,
    )
    return card

# read the model catalog entries
with open(team_config_path) as fobj:
    members = yaml.safe_load(fobj)

# sort members by first name
members = sorted(members, key=lambda m: m['name'])

# loop and process each model
cards = ""
for member_info in members:
    print(member_info)
    
    # add link to team index
    card_md = generate_member_card_content(member_info)
    cards += card_md

# write team list index page
print(cards)
with mkdocs_gen_files.open(team_list_path, 'w') as f:
    f.write(TEAM_LIST_TEMPLATE.format(cards=cards))
