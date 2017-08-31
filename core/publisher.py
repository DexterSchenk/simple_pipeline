import re
import pprint
import os
import subprocess
import copy
import shutil
import logging

import ui
import utils
import templates

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
        data = copy.deepcopy(self.env_info)
        utils.update_dict(data, self.ui.get_values_from_widgets())
        version_path = templates.construct_path(data)
        data.pop('version')
        master_path = templates.construct_path(data)

        version_path = self._publish_version(version_path)
        self._publish_master(version_path, master_path)

        self.notify(data, version_path, master_path)

        cmds.confirmDialog(title='Publish done', button=['Close'], cancelButton='Close', dismissString='Close',
                           message='Published the following files:\n{}\n{}'.format(version_path, master_path))

    def _publish_version(self, path):
        logging.info("Publishing version to path: {}".format(path))
        return self.export(path)

    def _publish_master(self, version_path, master_path):
        logging.info("Publishing master to path:  {}".format(master_path))
        if os.path.exists(version_path):
            shutil.copy(version_path, master_path)
        else:
            raise IOError("Version file is missing: {}".format(version_path))

    def notify(self, data, version_path, master_path):
        logging.info("Published with the following data:\n{}".format(pprint.pformat(data)))
        logging.info("Published paths:")
        logging.info("Version path: {}".format(version_path))
        logging.info("Master path:  {}".format(master_path))

    def export(self, path):
        pass
