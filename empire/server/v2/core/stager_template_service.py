import fnmatch
import importlib.util
import os
from typing import Optional

from sqlalchemy.orm import Session

from empire.server.common import helpers
from empire.server.database import models
from empire.server.database.base import SessionLocal


class StagerTemplateService(object):
    def __init__(self, main_menu):
        self.main_menu = main_menu

        # loaded stager format:
        #     {"stagerModuleName": moduleInstance, ...}
        self._loaded_stager_templates = {}

        with SessionLocal.begin() as db:
            self._load_stagers(db)

    def new_instance(self, template: str):
        instance = type(self._loaded_stager_templates[template])(self.main_menu)
        for key, value in instance.options.items():
            if value.get("SuggestedValues") is None:
                value["SuggestedValues"] = []
            if value.get("Strict") is None:
                value["Strict"] = False

        return instance

    def get_stager_template(
        self, name: str
    ) -> Optional[object]:  # would be nice to have a BaseListener object.
        return self._loaded_stager_templates.get(name)

    def get_stager_templates(
        self,
    ):  # todo not sure if these should return .items or the raw dict
        return self._loaded_stager_templates.items()

    def _load_stagers(self, db: Session):
        """
        Load stagers from the install + "/stagers/*" path
        """
        root_path = "%s/stagers/" % db.query(models.Config).first().install_path
        pattern = "*.py"

        print(helpers.color("[*] v2: Loading stagers from: %s" % (root_path)))

        for root, dirs, files in os.walk(root_path):
            for filename in fnmatch.filter(files, pattern):
                file_path = os.path.join(root, filename)

                # don't load up any of the templates
                if fnmatch.fnmatch(filename, "*template.py"):
                    continue

                # extract just the module name from the full path
                stager_name = file_path.split("/stagers/")[-1][0:-3]

                # instantiate the module and save it to the internal cache
                spec = importlib.util.spec_from_file_location(stager_name, file_path)
                mod = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(mod)

                stager = mod.Stager(self.main_menu, [])
                for key, value in stager.options.items():
                    if value.get("SuggestedValues") is None:
                        value["SuggestedValues"] = []
                    if value.get("Strict") is None:
                        value["Strict"] = False

                self._loaded_stager_templates[slugify(stager_name)] = stager


def slugify(stager_name: str):
    return stager_name.lower().replace("/", "_")
