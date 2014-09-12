import os
import json


# Defaults
config = {
    'root': '~/nomadic',
    'port': 9137,
    'default_notebook': ''
}

# Create default config if necessary.
cfg_path = os.path.expanduser(u'~/.nomadic')
if not os.path.exists(cfg_path):
    with open(cfg_path, 'w') as cfg_file:
        json.dump(config, cfg_file)

# Open the config file.
with open(cfg_path, 'r') as cfg_file:
    user_cfg = json.load(cfg_file)
    config.update(user_cfg)

config['root'] = os.path.expanduser(config['root'])

# Load the config vals onto the module.
for key, val in config.items():
    globals()[key.upper()] = val
