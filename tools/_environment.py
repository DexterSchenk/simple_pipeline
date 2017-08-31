import sys
import os
import re
import shutil
import filecmp

pipeline_root = os.sep.join(re.split('[\\\/]', __file__)[:-2])
root = pipeline_root.rsplit(os.sep, 1)[0]


def _set_env(key, value):
    os.environ[key] = value
    print "Setting '${}' to '{}'".format(key, value)

def _setup_syspath():
    _set_env('PIPELINE_ROOT', pipeline_root)
    if pipeline_root not in sys.path:
        sys.path.append(pipeline_root)
        os.environ['PYTHONPATH'] = "%PYTHONPATH%;{}".format(pipeline_root)


def _setup_maya_shelves():
    path = os.path.join(pipeline_root, 'maya', 'shelves')
    _set_env('MAYA_SHELVES_PATH', path)


def _setup_envion_vars():
    _set_env('root', root)


def _create_workspace():
    source = os.path.join(pipeline_root, 'maya', 'workspace.mel')
    target = os.path.join(root, 'workspace.mel')
    os.environ['MAYA_WORKSPACE'] = target
    copy = True
    if os.path.exists(target):
        if filecmp.cmp(source, target):
            copy = False

    if copy:
        print "Copying {} to {}".format(source, target)
        shutil.copy(source, target)


def _get_maya_path():
    path = 'c:/Program Files/Autodesk/Maya2017/bin/maya.exe'
    _set_env("MAYA_EXE", path)

def setup():
    _setup_syspath()
    _create_workspace()
    _setup_maya_shelves()
    _get_maya_path()
    _setup_envion_vars()
