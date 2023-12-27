import glob
import copy
import json

cache_folder = '/assets/apple'
custom_folder = '/assets/custom_emojis'


rule_template = {
      "id": "INSERT_UNIQUE_INT",
      "priority": 2,
      "action": {
        "type": "redirect",
        "redirect": {
            "extensionPath": "/assets/FOLDER/EMOJI_URL.EXT"
        }
        },
      "condition": {
        "urlFilter": "https://chat.channable.com/static/emoji/EMOJI_URL.png",
        "resourceTypes": ["image"]
        }
    }

static_rules = []

# Create a rule for every Apple emoji
for rule_id, apple_file in enumerate(glob.glob(f'.{cache_folder}/*.png'), 1):
    temp_rule = copy.deepcopy(rule_template)
    emoji_code = apple_file.split('/')[-1].split('.')[0]

    temp_rule["id"] = rule_id
    temp_rule["action"]["redirect"]["extensionPath"] = f"{cache_folder}/{emoji_code}.png"
    temp_rule["condition"]["urlFilter"] = f"https://chat.channable.com/static/emoji/{emoji_code}.png"

    static_rules.append(temp_rule)

# Create a rule for every custom emoji
for rule_id, custom_file in enumerate(glob.glob(f'.{custom_folder}/*'), rule_id+1):
    temp_rule = copy.deepcopy(rule_template)
    emoji_code, local_extension = custom_file.split('/')[-1].split('.')

    temp_rule["id"] = rule_id
    temp_rule["action"]["redirect"]["extensionPath"] = f"{custom_folder}/{emoji_code}.{local_extension}"
    temp_rule["condition"]["urlFilter"] = f"https://chat.channable.com/api/v4/emoji/{emoji_code}/image"

    static_rules.append(temp_rule)

with open('static_rules.json','w') as json_file:    
    json.dump(static_rules, json_file, indent=2)
