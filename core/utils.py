import os
import json
import re
import collections


class Format:
    # Regex formatting
    numeric = re.compile(r'[^\d.]+')

    def __init__(self):
        pass

    @classmethod
    def strip_non_decimal(cls, string):
        return cls.numeric.sub('', string)


def load_json(path):
    path = os.path.normpath(path)
    with open(path, 'rb') as stream:
        return json.load(stream)


def load_config(path):
    if not re.search(r"^\w:\\", path):
        path = get_path("PIPELINE_ROOT", 'config', path)
    return load_json(path)


def get_path(env, *args):
    return os.path.normpath(os.sep.join([os.environ[env]] + list(args)))


def get_latest_version(path):
    regexes = load_config('regexes.json')
    regex = regexes['version']
    # regex = regexes['version'].replace('\\b', '').replace('(?i)', '')
    path = os.path.normpath(path)
    dirpath = os.path.dirname(path)
    filename = os.path.basename(path)
    files = os.listdir(dirpath)
    file_regex = re.sub(regex, regex.replace('\\', '\\\\'), filename)

    versions = []
    for f in files:
        if re.search(file_regex, f):
            versions.append(f)
    if versions:
        versions.sort()
        version_number = int(Format.strip_non_decimal(re.search(regex, versions[-1]).group()))
        latest_version = re.sub(regex, 'v{0:02}'.format(version_number + 1), filename)
        return os.path.join(dirpath, latest_version)
    else:
        return path


# Complex dictionary tools


def update_dict(original, new, skip_none=False):
    for k, v in new.iteritems():
        if isinstance(v, collections.Mapping):
            r = update_dict(original.get(k, {}), v, skip_none=skip_none)
            if r is None and skip_none:
                continue
            original[k] = r
        else:
            if new[k] is None and skip_none:
                continue
            try:
                original[k] = new[k]
            except TypeError:
                original = new[k]
    return original


def get_key_name(name, key):
        if name:
            if key:
                return name + '-' + key
            else:
                return name
        else:
            return key


def build_dict_with_keys(keys=[], dictionary={}, value=None):
    """
    Build and update a given dictionary with a list of keys and a end value
    :param keys: list of keys
    :param dictionary: dictionary to update/build
    :param value: end value of dictionary
    :return: result of search
    """
    def recurse(cur, d):
        cur_key = keys[cur]
        if cur == len(keys) - 1:
            try:
                # End of keys found, set value
                d[cur_key] = value
                return d
            except KeyError:
                # Adding sub-dict
                d.update({cur_key: value})
            except TypeError:
                # Value found where dictionary expected, moving current value to blank entry ('')
                d = {'': d, cur_key: value}
            return d

        if cur_key in d.keys():
            # Existing sub-dict found, updating
            d.update({cur_key: recurse(cur+1, d[cur_key])})
        else:
            # Create sub-dict
            d.update({cur_key: {}})
            d[cur_key].update(recurse(cur+1, d[cur_key]))
        return d

    return recurse(0, dictionary)


def build_dict_with_long_keys(name, dictionary):
    """
    Traverse a dictionary and return a key, value pair with the traversed depth as the key, separated by '-'
    dictionary:
        {
            'dash-separated-key': 'value',
            'dash-separated': 'value'
        }
    :param name: base name of key
    :param dictionary: Dictionary to traverse
    :return: dict: flattened dictionary
    """
    flat_dict = {}
    for k, v in sorted(dictionary.items()):
        if type(v) is dict:
            d = build_dict_with_long_keys(get_key_name(name, k), v)
            flat_dict.update(d)
        else:
            flat_dict.update({get_key_name(name, k): v})
    return flat_dict
