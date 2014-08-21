import os
import json

cfg_path = os.path.expanduser(u'~/.nomadic')

config = {
    'notes_path': '~/nomadic',
    'port': 9137
}

# Create default config if necessary.
if not os.path.exists(cfg_path):
    with open(cfg_path, 'w') as cfg_file:
        json.dump(config, cfg_file)

# Open the config file.
with open(cfg_path, 'r') as cfg_file:
    user_cfg = json.load(cfg_file)

config.update(user_cfg)

notes_path = os.path.expanduser(config['notes_path'])

# Create the notes directory if necessary.
if not os.path.exists(notes_path):
    os.makedirs(notes_path)

config['notes_path'] = notes_path
