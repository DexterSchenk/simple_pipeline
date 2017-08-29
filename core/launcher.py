import re
import pprint

import os
import subprocess
import copy

import ui
import utils
import templates


class Launcher(object):
    def __init__(self, template, env_info, **kwargs):
        self.ui = ui.SimpleUI(template=template)
        self.ui.action = self.launch
        self.env_info = env_info

        self.other = kwargs

    def run(self):
        print "SHOWING UI"
        self.ui.run()
        print "DONE SHOWING UI"

    def launch(self):
        data = copy.deepcopy(self.env_info)
        utils.update_dict(data, self.ui.get_values_from_widgets())
        pprint.pprint(data)
        scenepath = templates.construct_path(data)
        self.launch_maya(scenepath=scenepath)

    def launch_maya(self, scenepath):
        print "Opening {}".format(scenepath)
        open_file = True
        if 'filetype' in templates.deconstruct(scenepath):
            if not os.path.exists(scenepath):
                scenepath = scenepath.rsplit(os.sep , 1)[0]
                open_file = False

        print "Running Maya..."
        if open_file:
            print "{} -file {}".format(os.environ['MAYA_EXE'], scenepath)
        else:
            print "{} -proj {}".format(os.environ['MAYA_EXE'], scenepath)

