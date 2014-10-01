import os
import json


# Defaults
config = {
    'root': '~/nomadic',
    'port': 9137,
    'default_notebook': '',
    'override_stylesheet': ''
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

# Expand user paths.
for key in ['root', 'override_stylesheet']:
    config[key] = os.path.expanduser(config[key])

# Load the config vals onto the module.
for key, val in config.items():
    globals()[key.upper()] = val
