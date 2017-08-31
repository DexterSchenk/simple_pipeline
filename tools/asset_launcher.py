import sys
import os
import re

import _environment

#todo: remove for production
tmp_path = r'C:\Users\Dexter\PycharmProjects\simple_pipeline'

if os.path.exists(tmp_path):
    _environment.root = 'H:\work'

_environment.setup()

import core.launcher
import core.utils
import core.templates


def get_assets(info):
    assets = {}
    asset_root = core.templates.construct_path(info, template='asset-root')
    for t in os.listdir(asset_root):
        if re.search(core.templates.regex_templates['type'], t):
            assets.update({t: []})
            for a in os.listdir(os.path.join(asset_root, t)):
                if re.search(core.templates.regex_templates['asset'], a):
                    assets[t].append(a)
    if assets:
        print "Found {} assets".format(len([a for a in assets.values()]))
        return assets
    else:
        raise IOError("No assets found in {}".format(asset_root))


def launch():

    def update_assets():
        type_widget = launcher.ui.get_widget('type')
        asset_widget = launcher.ui.get_widget('asset')
        asset_widget.clear()
        asset_widget.addItems(assets[launcher.ui._get_value(type_widget)])

    template = core.utils.load_config('asset_launcher.json')

    # info = {'root': os.environ['root'], 'version': 'v01', 'filetype': 'ma'}
    info = {
        'root': os.environ['root'],
        'filetype': 'ma',
        'context': 'asset_dev',
        'version': 'v00'
    }

    assets = get_assets(info)

    for i in template['objects']:
        if i['name'] == 'asset':
            # i['values'] = [inner for outer in assets.values() for inner in outer]
            i['values'] = assets[assets.keys()[0]]
        if i['name'] == 'type':
            i['values'] = assets.keys()

    launcher = core.launcher.Launcher(template=template, env_info=info, asset_lookup=assets)

    launcher.ui.get_widget('type').currentIndexChanged.connect(update_assets)

    launcher.run()


launch()
