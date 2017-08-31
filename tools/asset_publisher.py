import sys
import os
import re

import pprint

import _environment

#todo: remove for production
_environment.root = 'H:\work'

_environment.setup()

import core.publisher
import core.utils
import core.templates
import core._maya

import maya.cmds as cmds


def check_scene(info, scenepath):
    if 'asset' not in info:
        example_info = {
            "root": os.environ['root'],
            "context": "asset_dev",
            "asset": "Ch_Axolotl",
            "version": "v01",
            "type": "chars",
            "step": "model",
            "filetype": "ma",
            "shot": "Sc_001"
        }
        cmds.confirmDialog(title='ERROR', button=['Close'], cancelButton='Close', dismissString='Close',
                           message="You're scene is isn't in the correct folder stucture!\n"
                                   "Scene path:       {}\n"
                                   "Expected example: {}".format(scenepath,
                                                                 core.templates.construct_path(example_info)))
        raise OSError("Invalid scene location: {}".format(scenepath))

    if cmds.file(q=True, modified=True):
        cmds.confirmDialog(title='ERROR', button=['Close'], cancelButton='Close', dismissString='Close',
                           message='ERROR: Please save your scene before publishing!')
        raise RuntimeError("Scene isn't saved")


def export(path):
    return core._maya.export(path, selection=True, construction_history=False)


def publish():
    template = core.utils.load_config('asset_publisher.json')

    # scenepath = "h:/work/asset_dev/props/Pr_salmon_sosaties/rig/Pr_salmon_sosaties-rig-v01.ma"
    scenepath = cmds.file(sn=True, q=True)

    info = core.templates.deconstruct(scenepath)

    pprint.pprint(info)

    info['filetype'] = 'ma'
    info['context'] = 'assetbuilds'
    info['version'] = 'v01'

    version_path = core.templates.construct_path(info)
    latest_version_path = core.utils.get_latest_version(version_path)
    info = core.templates.deconstruct(latest_version_path)

    check_scene(info, scenepath)

    publisher = core.publisher.Publisher(template=template, env_info=info, scenepath=scenepath)
    publisher.ui.update_widgets(info)

    publisher.export = export

    publisher.run()

if __name__ == '__main__':
    publish()
