import pprint
import re
import os
import logging


import utils

pipeline_root = os.sep.join(re.split('[\\\/]', __file__)[:-2])
path_templates = utils.load_json(pipeline_root + "/config/paths.json")
regex_templates = utils.load_json(pipeline_root + "/config/regexes.json")


def construct_path(info, template=None, get_best_path=True):
    if template:
        try:
            return path_templates[template].format(**info)
        except:
            logging.error("Can't build path from template '{}': '{}' with the following info:\n"
                          "{}\n"
                          "".format(template, path_templates[template], pprint.pformat( info)))
            raise

    paths = []
    for name, template in path_templates.items():
        try:
            p = template.format(**info)
            template_keys = name.split('-')
            if p and not re.search('[{}]', p):
                if info['context'] in template_keys:
                    paths.append(os.path.normpath(p))
        except KeyError:
            pass

    paths.sort(key=len)
    if paths:
        if len(paths) > 1 and get_best_path is False:
            logging.error(
                "Found too many paths:\nInfo:\n{}\n\nPaths:\n{}".format(pprint.pformat(info), pprint.pformat(paths)))
        else:
            if len(paths) > 1:
                logging.warning("Built multiple paths, using longest path:\nPaths:\n{}".format(pprint.pformat(paths)))
            return paths[-1]
    else:
        logging.error("Failed to get any paths:\nInfo:\n{}".format(pprint.pformat(info)))


def deconstruct(string):
    info = {}
    try:
        for name, regex in regex_templates.items():
            result = re.search(regex, string)
            if result:
                if any(v for v in result.groupdict().values()):
                    for k, v in result.groupdict().items():
                        if v:
                            info.update({name: k})
                            break
                else:
                    info.update({name: result.group()})
    except:
        logging.error("Failed to deconstruct string: {}".format(string))
        raise
    return info
