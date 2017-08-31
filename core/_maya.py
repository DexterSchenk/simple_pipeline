import logging

import maya.cmds as cmds


def export(path, selection=False, construction_history=False, force=False, filetype='ma'):
    if filetype == 'ma':
        filetype = 'mayaAscii'
    elif filetype == 'mb':
        filetype = 'mayaBinary'
    else:
        raise ValueError("Invalid filetype: {}. Expecting 'ma' or 'mb'".format(filetype))
    if selection:
        exported_path = cmds.file(path, exportSelected=True, constructionHistory=construction_history, type=filetype,
                                  force=force)
    else:
        exported_path = cmds.file(path, exportAll=True, constructionHistory=construction_history, type=filetype,
                                  force=force)
    logging.info("Exported {}".format(path))
    return exported_path
