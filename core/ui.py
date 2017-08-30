import sys
try:
    from PySide2.QtWidgets import *
    from PySide2.QtCore import *
    from PySide2.QtGui import *
except ImportError:
    from PySide.QtCore import *
    from PySide.QtGui import *

import widget_builders as sun_wd
import utils

import pprint

import logging

__author__ = 'dexterschenk'

# Setup Logging
logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger(__name__)


class GUI(QDialog):

    def build_window(self, data):
        def get_winsize(size_data, axis):
            s = size_data[axis]
            s_max = s
            s_min = s
            try:
                s = min(s, size_data['max'][axis])
                s_max = size_data['max'][axis]
            except KeyError:
                pass
            try:
                s = min(s, size_data['min'][axis])
                s_min = size_data['min'][axis]
            except KeyError:
                pass
            return s, s_min, s_max

        self.setWindowTitle(data['info']['name'])

        x = get_winsize(data['info']['size'], 'x')
        y = get_winsize(data['info']['size'], 'y')

        self.setMinimumSize(x[1], y[1])
        self.setMaximumSize(x[2], y[2])
        self.setBaseSize(x[0], x[1])

    def align_qt_labels(self, widgets=None):
        if widgets is None:
            widgets = self.qt_widgets

        max_width = 0
        for widget in widgets:
            widget = self._get_component_widget(widget, component=None, widget_type=QLabel)
            if widget is None:
                continue
            max_width = max(widget.sizeHint().width(),max_width)

        for widget in widgets:
            widget = self._get_component_widget(widget, component=None, widget_type=QLabel)
            if widget is None:
                continue
            widget.setMinimumWidth(max_width + 5)

    def build_qt_widget(self, data, default_as_label=False):
        try:
            t = data['type']
        except KeyError:
            t = 'label'

        # Create QtWidget from data type

        qt_obj = None

        if t == 'label':
            qt_obj = sun_wd.label(data)
        elif t == 'text':
            qt_obj = sun_wd.text(data)
        elif t == 'spinner':
            qt_obj = sun_wd.spinner(data)
        elif t == 'combobox':
            qt_obj = sun_wd.combobox(data)
        elif default_as_label:
            qt_obj = sun_wd.label(data)
            t = 'label'

        if qt_obj is None:
            raise ValueError("Specified widget type '{0}' does not exist!".format(t))

        if t != 'label':
            try:
                qt_obj.component_name = data['name']
                try:
                    qt_obj.label = data['label']
                except KeyError:
                    qt_obj.label = data['name']
                try:
                    qt_obj.required = data['required']
                except KeyError:
                    qt_obj.required = True
                try:
                    qt_obj.regex = data['regex']
                except KeyError:
                    qt_obj.regex = None
            except KeyError:
                raise KeyError("{0} is missing a 'name' key: value!".format(data))

        if t != 'label' and 'label' in data:
            hbox = QHBoxLayout()
            label = sun_wd.label(data)
            hbox.addWidget(label)
            hbox.addWidget(qt_obj)

            return hbox

        return qt_obj

    def _get_component_widget(self, widget, component='component_name', widget_type=None):
        if isinstance(widget, QHBoxLayout):
            for lw in self._get_layout_widgets(widget):
                widget = lw.widget()
                if widget_type:
                    if isinstance(widget_type, list):
                        pass
                    if not isinstance(widget, widget_type):
                        continue
                if component:
                    if hasattr(widget, component):
                        return widget
                else:
                    return widget

    def _get_value(self, widget):
        for attr in ['text', 'value', 'currentText', ]:
            try:
                func = getattr(widget, attr)
                return func()
            except AttributeError:
                continue
        else:
            raise AttributeError("{0} has no defined value return function!".format(widget.__class__.__name__))

    def _set_value(self, widget, value):
        for attr in ['setText', 'setValue', 'findText']:
            try:
                func = getattr(widget, attr)
                if attr == 'findText':
                    value = func(value)
                    func = getattr(widget, 'setCurrentIndex')
                return func(value)
            except AttributeError:
                continue
        else:
            raise AttributeError("{0} has no defined value return function!".format(widget.__class__.__name__))

    def _get_layout_widgets(self, layout):
        return (layout.itemAt(i) for i in range(layout.count()))

    def get_widget(self, name):
        for widget in self.qt_widgets:
            widget = self._get_component_widget(widget)
            if widget is None:
                continue
            if widget.component_name == name:
                return widget

    def get_values_from_widgets(self):
        info_dict = {}
        for widget in self.qt_widgets:
            widget = self._get_component_widget(widget)
            if widget is None:
                continue

            val = self._get_value(widget)

            if val or widget.required:
                if not val:
                    QErrorMessage(self).showMessage("Missing field! {0}".format(widget.label))
                    return None

                # Force validation of required fields
                if widget.regex:
                    status = widget.validator().validate(val, 0)

                    if status[0] != QValidator.State.Acceptable:
                        QErrorMessage(self).showMessage("Invalid field! {0}: '{1}'".format(widget.label, val))
                        return None

                info_dict = utils.build_dict_with_keys(keys=widget.component_name.split('-'),
                                                       value=val,
                                                       dictionary=info_dict)

        return info_dict

    def update_widgets(self, data=None):
        for widget in self.qt_widgets:
            widget = self._get_component_widget(widget)
            if widget:
                try:
                    self._set_value(widget, data[widget.component_name])
                except KeyError:
                    log.warning("Could not set field '{0}'".format(widget.component_name))

    def run(self):
        ''' Run the app and show the main form. '''
        self.exec_()


class SimpleUI(GUI):
    ''' An example application for PyQt. Instantiate
        and call the run method to run. '''

    def __init__(self, template):
        # create a Qt application --- every PyQt app needs one
        self.qt_app = QApplication(sys.argv)

        # Call the parent constructor on the current object
        QDialog.__init__(self, None)
        data_objects = template['objects']

        self.qt_widgets = []

        # Build widget list
        for obj in data_objects:
            self.qt_widgets.append(self.build_qt_widget(data=obj))

        self.init_ui(template)

    def init_ui(self, template):

        # Set up the window
        self.build_window(template)

        # Build run button
        self.action_button = QPushButton("Run")
        self.action_button.clicked.connect(self.action)

        # Build a vertical layout
        self.vbox = QVBoxLayout()

        # Add widgets/layouts to vertical layout
        for widget in self.qt_widgets:
            if isinstance(widget, QHBoxLayout):
                self.vbox.addLayout(widget)
            else:
                self.vbox.addWidget(widget)
        self.align_qt_labels(widgets=self.qt_widgets)

        self.vbox.addWidget(self.action_button)
        # Use the vertical layout for the current window
        self.setLayout(self.vbox)

    def action(self):
        data = self.get_values_from_widgets()
        print data
