import re
import time
import pprint
import os
import subprocess
import copy
import shutil
import logging

import ui
import utils
import templates
import notifications

import maya.cmds as cmds


class Publisher(object):
    def __init__(self, template, env_info, scenepath=None, **kwargs):
        self.ui = ui.SimpleUI(template=template)
        self.ui.action = self.publish
        self.env_info = env_info
        if scenepath is None:
            self.path = cmds.file(sn=True, q=True)
        else:
            self.path = scenepath

        self.other = kwargs

    def run(self):
        logging.debug("SHOWING UI")
        self.ui.run()
        logging.debug("DONE SHOWING UI")

    def publish(self):
        logging.debug("PUBLISH START".center(50, '-'))
        data = copy.deepcopy(self.env_info)
        utils.update_dict(data, self.ui.get_values_from_widgets())
        version_path = templates.construct_path(data)

        master_data = copy.deepcopy(data)
        master_data.pop('version')
        master_path = templates.construct_path(master_data)

        version_path = self._publish_version(version_path)
        self._publish_master(version_path, master_path)

        capture_path = capture(data)

        self.notify(data, version_path, master_path, capture_path)

        cmds.confirmDialog(title='Publish done', button=['Close'], cancelButton='Close', dismissString='Close',
                           message='Published the following files:\n{}\n{}'.format(version_path, master_path))
        logging.debug("PUBLISH END".center(50, '-'))

    def _publish_version(self, path):
        logging.info("Publishing version to path: {}".format(path))
        return self.export(path)

    def _publish_master(self, version_path, master_path):
        logging.info("Publishing master to path:  {}".format(master_path))
        if os.path.exists(version_path):
            shutil.copy(version_path, master_path)
        else:
            raise IOError("Version file is missing: {}".format(version_path))

    def notify(self, data, version_path, master_path, capture_path):
        logging.debug("NOTIFY START".center(50, '-'))
        logging.info("Published with the following data:\n{}".format(pprint.pformat(data)))
        logging.info("Published paths:")
        logging.info("Version path: {}".format(version_path))
        logging.info("Master path:  {}".format(master_path))

        if 'asset' in data:
            name = data['asset']
            pub_type = data['type']
        else:
            name = data['shot']
            pub_type = 'shot'

        notifications.publish_notify(name=name, pub_type=pub_type, version=data['version'], path=version_path,
                                     message=data['message'], capture_path=capture_path)
        logging.debug("NOTIFY END".center(50, '-'))

    def export(self, path):
        pass


def capture(data):
    logging.info("CAPTURE START".center(50, '-'))
    if 'asset' in data:
        filename = "{}-{}".format(data['asset'], data['version'])
    else:
        filename = "{}-{}".format(data['shot'], data['version'])

    if cmds.getAttr("defaultRenderGlobals.imageFormat") != 8:
        cmds.setAttr("defaultRenderGlobals.imageFormat", 8)

    mov_data = copy.deepcopy(data)
    mov_data['filetype'] = 'mov'
    mov_path = templates.construct_path(mov_data)
    if 'asset' in data:
        path = cmds.playblast(f=filename, fmt="image", qlt=100, os=True, fo=True, fr=[1])
    else:
        path = cmds.playblast(f=filename, fmt="image", qlt=100, os=True, fo=True)

    if 'shot' in data:
       path = _ffmpeg(path, mov_path)
    else:
        path = path.replace('#', '0')
    capture_data = templates.deconstruct(path)


    if 'asset' in data:
        capture_data['context'] = 'assetbuilds'
        version_path = templates.construct_path(capture_data)
        logging.info("Copying {} to {}".format(path, version_path))
        shutil.copy(path, version_path)
    else:
        version_path = path

    capture_data.pop('version')
    master_path = templates.construct_path(capture_data)
    logging.info("Copying {} to {}".format(path, master_path))
    shutil.copy(path, master_path)

    logging.info("CAPTURE END".center(50, '-'))

    return version_path


def _ffmpeg(image_path, mov_path):

    padding = image_path.count('#')
    image_path = image_path.replace('#'*padding, '%0{}d'.format(padding))
    logging.info("Running ffmpeg on {} => {}".format(image_path, mov_path))
    ffmpeg_path = utils.get_path("PIPELINE_ROOT", 'ffmpeg.exe')
    cmd = ffmpeg_path + ' -y -r 24 -i ' + image_path + ' -qscale 1 ' + mov_path
    logging.debug(cmd)
    result = subprocess.Popen(cmd)
    wait = 0
    while not os.path.exists(mov_path) and wait < 600:
        time.sleep(0.1)
        wait += 1

    if os.path.exists(mov_path):
        logging.info("Created mov: {}".format(mov_path))
    else:
        logging.error("Failed to create mov: {}".format(mov_path))
        raise RuntimeError("Failed to create mov: {}".format(mov_path))
    return mov_path
