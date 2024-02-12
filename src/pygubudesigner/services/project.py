import sys
import os
import pathlib
import logging
import importlib

from pygubu.component.uidefinition import UIDefinition
from ..widgetdescr import WidgetMeta
from ..i18n import translator
from .stylehandler import StyleHandler


logger = logging.getLogger(__name__)
_ = translator


def load_custom_widget(path: pathlib.Path):
    if not path.match("*.py"):
        return
    dirname = str(path.parent)
    modulename = path.name[:-3]
    if dirname not in sys.path:
        sys.path.append(dirname)
    try:
        importlib.import_module(modulename)
    except Exception as e:
        logger.exception(e)
        raise e


class Project:
    """Store project data for designer."""

    def __init__(self):
        self.fpath = None
        self.uidefinition: UIDefinition = None
        self.custom_widgets: list = []
        self.settings: dict = {}

    def get_relative_path(self, path):
        return os.path.relpath(path, start=self.fpath.parent)

    def save(self, filename):
        self.fpath = pathlib.Path(filename)
        self.uidefinition.custom_widgets = self.custom_widgets
        self.uidefinition.project_settings = self.settings
        self.uidefinition.save(filename)

    def get_full_settings(self) -> dict:
        settings = self.settings.copy()
        cwlist = []
        for path in self.custom_widgets:
            cwlist.append(path)
        settings["custom_widgets"] = cwlist
        return settings

    def set_full_settings(self, new_settings: dict):
        self.custom_widgets = new_settings.pop("custom_widgets", [])
        self.settings = new_settings

    @staticmethod
    def load(filename) -> "Project":
        uidef = UIDefinition(wmetaclass=WidgetMeta)
        uidef.load_file(filename)

        uidir = pathlib.Path(filename).parent.resolve()

        # Load custom widgets
        path_list = []
        notfound_list = []
        # Xml will have relative paths to UI file directory
        for cw in uidef.custom_widgets:
            cw_path: pathlib.Path = pathlib.Path(uidir, cw).resolve()
            if cw_path.exists():
                path_list.append(cw_path)
            else:
                notfound_list.append(cw_path)
        if notfound_list:
            # Notify user some path does not exits
            # raise exception
            msg = "Custom widgets not found:\n" + "\n".join(
                (str(f) for f in notfound_list)
            )
            raise Exception(msg)
        else:
            # Load builders
            for path in path_list:
                load_custom_widget(path)

        # Load theme file
        theme_file = uidef.project_settings.get("ttk_style_definition_file", "")
        StyleHandler.clear_definition_file()
        if theme_file:
            theme_path: pathlib.Path = uidir / theme_file
            if theme_path.exists() and theme_path.is_file():
                # Load definitions file.
                StyleHandler.set_definition_file(theme_path)

        project = Project()
        project.fpath = filename
        project.uidefinition = uidef
        project.custom_widgets = uidef.custom_widgets
        project.settings = uidef.project_settings
        return project
