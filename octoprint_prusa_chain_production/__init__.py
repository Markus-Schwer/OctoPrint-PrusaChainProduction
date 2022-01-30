# coding=utf-8
from __future__ import absolute_import

import octoprint.plugin

class PrusaChainProductionPlugin(octoprint.plugin.StartupPlugin,
    octoprint.plugin.SettingsPlugin,
    octoprint.plugin.AssetPlugin,
    octoprint.plugin.TemplatePlugin
):
    def on_after_startup(self):
        self._logger.info("Hello World!")

    ##~~ SettingsPlugin mixin

    def get_settings_defaults(self):
        return {
            # put your plugin's default settings here
        }

    ##~~ AssetPlugin mixin

    def get_assets(self):
        # Define your plugin's asset files to automatically include in the
        # core UI here.
        return {
            "js": ["js/prusa_chain_production.js"],
            "css": ["css/prusa_chain_production.css"],
            "less": ["less/prusa_chain_production.less"]
        }

    ##~~ TemplatePlugin mixin

    # def get_template_configs(self):
    #     return [
    #         dict(type="generic", template="prusa_chain_production.jinja2", custom_bindings=True)
    #     ]

    ##~~ Softwareupdate hook

    def get_update_information(self):
        # Define the configuration for your plugin to use with the Software Update
        # Plugin here. See https://docs.octoprint.org/en/master/bundledplugins/softwareupdate.html
        # for details.
        return {
            "prusa_chain_production": {
                "displayName": "PrusaChainProduction Plugin",
                "displayVersion": self._plugin_version,

                # version check: github repository
                "type": "github_release",
                "user": "Markus-Schwer",
                "repo": "OctoPrint-PrusaChainProduction",
                "current": self._plugin_version,

                # update method: pip
                "pip": "https://github.com/Markus-Schwer/OctoPrint-PrusaChainProduction/archive/{target_version}.zip",
            }
        }


# If you want your plugin to be registered within OctoPrint under a different name than what you defined in setup.py
# ("OctoPrint-PluginSkeleton"), you may define that here. Same goes for the other metadata derived from setup.py that
# can be overwritten via __plugin_xyz__ control properties. See the documentation for that.
__plugin_name__ = "PrusaChainProduction Plugin"

# Starting with OctoPrint 1.4.0 OctoPrint will also support to run under Python 3 in addition to the deprecated
# Python 2. New plugins should make sure to run under both versions for now. Uncomment one of the following
# compatibility flags according to what Python versions your plugin supports!
#__plugin_pythoncompat__ = ">=2.7,<3" # only python 2
#__plugin_pythoncompat__ = ">=3,<4" # only python 3
#__plugin_pythoncompat__ = ">=2.7,<4" # python 2 and 3

def __plugin_load__():
    global __plugin_implementation__
    __plugin_implementation__ = PrusaChainProductionPlugin()

    global __plugin_hooks__
    __plugin_hooks__ = {
        "octoprint.plugin.softwareupdate.check_config": __plugin_implementation__.get_update_information
    }
