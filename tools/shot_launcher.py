import sys
import os
import re

import _environment

#todo: remove for production
_environment.root = 'H:\work'

_environment.setup()

import core.launcher
import core.utils
import core.templates


def get_shots(info):
    shots = []
    shot_root = core.templates.construct_path(info, template='shot-root')
    for s in os.listdir(shot_root):
        if re.search(core.templates.regex_templates['shot'], s):
            shots.append(s)
    if shots:
        print "Found {} shots".format(len(shots))
        return shots
    else:
        raise IOError("No shots found in {}".format(shot_root))


def launch():
    template = core.utils.load_config('shot_launcher.json')

    # info = {'root': os.environ['root'], 'version': 'v01', 'filetype': 'ma'}
    info = {
        'root': os.environ['root'],
        'filetype': 'ma',
        'context': 'shots',
        'version': 'v00'
    }

    shots = get_shots(info)

    for i in template['objects']:
        if i['name'] == 'shot':
            i['values'] = shots
            break

    launcher = core.launcher.Launcher(template=template, env_info=info)

    launcher.run()


launch()
