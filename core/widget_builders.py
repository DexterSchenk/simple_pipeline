try:
    from PySide2.QtWidgets import *
    from PySide2.QtCore import *
    from PySide2.QtGui import *
except ImportError:
    from PySide.QtCore import *
    from PySide.QtGui import *


def _get_field(data, field, data_type):
    try:
        return data_type(data[field])
    except KeyError:
        return None


def _apply_validator(qt_obj, data):
    if 'regex' in data:
        regex = QRegExp(data['regex'])
        rx = QRegExpValidator(regex)
        qt_obj.setValidator(rx)


###########################################################
# Custom Widgets
###########################################################

class MySpinBox(QSpinBox):
    def __init__(self, *args):
        QSpinBox.__init__(self, *args)

        self.setRange(0, 99)

    def textFromValue(self, value):
        return "%02d" % value


###########################################################
# Widgets
###########################################################


def label(data):
    qt_obj = QLabel(_get_field(data, 'label', str))
    return qt_obj


def text(data):
    qt_obj = QLineEdit(_get_field(data, 'text', str))

    key = 'readonly'
    if key in data:
        qt_obj.setEnabled(not _get_field(data, key, int))

    if 'mask' in data.keys():
        if isinstance(qt_obj, QLineEdit):
            qt_obj.setInputMask(data['mask'])
    _apply_validator(qt_obj, data)
    return qt_obj


def spinner(data):
    qt_obj = MySpinBox()

    key = 'readonly'
    if key in data:
        qt_obj.setEnabled(not _get_field(data, key, int))

    # Values
    key = 'value'
    if key in data:
        qt_obj.setValue(_get_field(data, key, int))
    key = 'step'
    if key in data:
        qt_obj.setSingleStep(_get_field(data, key, int))
    key = 'min'
    if key in data:
        qt_obj.setMinimum(_get_field(data, key, int))
    key = 'max'
    if key in data:
        qt_obj.setMaximum(_get_field(data, key, int))

    # Format
    key = 'prefix'
    if key in data:
        qt_obj.setPrefix(_get_field(data, key, str))
    key = 'suffix'
    if key in data:
        qt_obj.setSuffix(_get_field(data, key, str))

    return qt_obj


def combobox(data):
    qt_obj = QComboBox()

    key = 'readonly'
    if key in data:
        qt_obj.setEnabled(not _get_field(data, key, int))

    key = 'values'
    if key in data:
        qt_obj.addItems(data[key])

    return qt_obj


def checkbox(data):
    qt_obj = QCheckBox(_get_field(data, 'checkbox', str))

    key = 'readonly'
    if key in data:
        qt_obj.setEnabled(not _get_field(data, key, int))

    key = 'value'
    if key in data:
        qt_obj.setChecked(data[key])
    return qt_obj
