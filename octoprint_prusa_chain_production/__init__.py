# coding=utf-8
from __future__ import absolute_import

import octoprint.plugin
import requests


class PrusaChainProductionPlugin(octoprint.plugin.SettingsPlugin,
                                 octoprint.plugin.StartupPlugin,
                                 octoprint.plugin.AssetPlugin,
                                 octoprint.plugin.TemplatePlugin,
                                 octoprint.plugin.SimpleApiPlugin):
    server_url = None

    def control_device(self, name, cmd):
        trimmed_server_url = self.server_url
        # trim trailing slashes
        if trimmed_server_url.endswith('/'):
            trimmed_server_url = trimmed_server_url[:-1]

        requests.get("{}/{}/{}".format(trimmed_server_url, name,
                                       "1" if cmd == "true" else "0"))

    ##~~ AssetPlugin mixin

    def on_after_startup(self):
        self.server_url = self._settings.get(["server_url"])
        self._logger.info("server_url = {}".format(self.server_url))

    ##~~ SettingsPlugin mixin

    def get_settings_defaults(self):
        return dict(server_url="http://prusa_chain")

    def on_settings_save(self, data):
        octoprint.plugin.SettingsPlugin.on_settings_save(self, data)
        self.server_url = self._settings.get(["server_url"])

    def on_settings_initialized(self):
        self.server_url = self._settings.get(["server_url"])

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

    def get_template_configs(self):
        return [
            dict(type="generic",
                 template="prusa_chain_production_controls.jinja2"),
            dict(type="settings",
                 template="prusa_chain_production_settings.jinja2"),
            dict(type="sidebar",
                 icon="plug",
                 template="prusa_chain_production_sidebar.jinja2")
        ]

    ##~~ SimpleApiPlugin mixin

    def get_api_commands(self):
        return dict(eject=[], reset=[], setFan=["enabled"], setLed=["enabled"])

    def on_api_command(self, command, data):
        if command == "eject":
            self.control_device("eject", "true")
        elif command == "reset":
            self.control_device("reset", "true")
        elif command == "setFan":
            self.control_device("fan", data["enabled"])
        elif command == "setLed":
            self.control_device("led", data["enabled"])

    # def on_api_get(self, request):
    #     self._logger.debug("on_api_get({}).Json: ".format(request, request.get_json()))
    #     if request == "getLightValues":
    #         response = dict()
    #         for pin in self.Lights:
    #             response(pin=self.Lights[pin]["value"])
    #         return flask.jsonify(response)

    def is_api_adminonly(self):
        return True

    ##~~ Softwareupdate hook

    def get_update_information(self):
        # Define the configuration for your plugin to use with the Software Update
        # Plugin here. See https://docs.octoprint.org/en/master/bundledplugins/softwareupdate.html
        # for details.
        return {
            "prusa_chain_production": {
                "displayName":
                "PrusaChainProduction Plugin",
                "displayVersion":
                self._plugin_version,

                # version check: github repository
                "type":
                "github_release",
                "user":
                "Markus-Schwer",
                "repo":
                "OctoPrint-PrusaChainProduction",
                "current":
                self._plugin_version,

                # update method: pip
                "pip":
                "https://github.com/Markus-Schwer/OctoPrint-PrusaChainProduction/archive/{target_version}.zip",
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
__plugin_pythoncompat__ = ">=2.7,<4"  # python 2 and 3


def __plugin_load__():
    global __plugin_implementation__
    __plugin_implementation__ = PrusaChainProductionPlugin()

    global __plugin_hooks__
    __plugin_hooks__ = {
        "octoprint.plugin.softwareupdate.check_config":
        __plugin_implementation__.get_update_information
    }
