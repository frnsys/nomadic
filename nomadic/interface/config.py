import os
import json

def load():
    cfg_path = os.path.expanduser(u'~/.nomadic')

    # Create default config if necessary.
    if not os.path.exists(cfg_path):
        with open(cfg_path, 'w') as cfg_file:
            json.dump({
                'notes_dir': '~/nomadic'
            }, cfg_file)

    with open(cfg_path, 'r') as cfg_file:
        cfg = json.load(cfg_file)

    notes_path = os.path.expanduser(cfg['notes_dir'])
    cfg['notes_dir'] = notes_path
    cfg['build_dir'] = os.path.join(notes_path, u'.build')

    # Create the notes directory if necessary.
    if not os.path.exists(notes_path):
        os.makedirs(notes_path)

    return cfg
