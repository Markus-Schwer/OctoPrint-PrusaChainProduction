# coding=utf-8
from __future__ import absolute_import

import octoprint.plugin
import requests
import threading
import flask
import time


class PrusaChainProductionPlugin(octoprint.plugin.SettingsPlugin,
                                 octoprint.plugin.StartupPlugin,
                                 octoprint.plugin.AssetPlugin,
                                 octoprint.plugin.TemplatePlugin,
                                 octoprint.plugin.EventHandlerPlugin,
                                 octoprint.plugin.SimpleApiPlugin):
    state = dict(
        errorOrClosed=True,
        ejecting=False,
        fansOn=False,
        ledsOn=False,
        coolingTimeLeft=None
    )
    coolingStartTime=None

    def connect(self):
        # TODO: fetch fan and led status from ejector
        self.state = dict(
            errorOrClosed=False,
            ejecting=False,
            fansOn=False,
            ledsOn=False,
            coolingTimeLeft=None
        )

    def disconnect(self):
        # reset status when disconnecting
        self.state = dict(
            errorOrClosed=True,
            ejecting=False,
            fansOn=False,
            ledsOn=False,
            coolingTimeLeft=None
        )

    def eject(self):
        self.state["ejecting"] = True

        self.set_fan(True)

        self.coolingStartTime = time.monotonic()
        self.state["coolingTimeLeft"] = self._settings.get(["coolingTime"])

    def cancel_eject(self):
        self.state["ejecting"] = False
        self.set_fan(False)

    def set_fan(self, enabled):
        self.state["fansOn"] = enabled

    def set_led(self, enabled):
        self.state["ledsOn"] = enabled

    ##~~ EventHandlerPlugin mixin

    def on_event(self, event, payload):
        if event == "PrintDone":
            # non-blocking eject
            threading.Thread(target=eject, args=(self.server_url, "eject", True))

            # send message to frontend, to update its state
            self._plugin_manager.send_plugin_message(self._identifier, dict())

    ##~~ StartupPlugin mixin

    def on_after_startup(self):
        self.connect()

    ##~~ SettingsPlugin mixin

    def get_settings_defaults(self):
        return dict(
            serialPort="/dev/ttyS0",
            ejectionTemp=15,
            coolingTime=900
        )

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
                 icon="cogs",
                 template="prusa_chain_production_sidebar.jinja2",
                 template_header="prusa_chain_production_sidebar_header.jinja2")
        ]

    ##~~ SimpleApiPlugin mixin

    def get_api_commands(self):
        return dict(connect=[], disconnect=[], eject=[], stop_eject=[], setFan=["enabled"], setLed=["enabled"])

    def on_api_command(self, command, data):
        if command == "connect":
            self.connect()
        if command == "disconnect":
            self.disconnect()
        if command == "eject":
            self.eject()
        elif command == "stop_eject":
            self.cancel_eject()
        elif command == "setFan":
            self.set_fan(data["enabled"])
        elif command == "setLed":
            self.set_led(data["enabled"])

        # send message to frontend, to update its state
        self._plugin_manager.send_plugin_message(self._identifier, dict())

    def on_api_get(self, request):
        if (self.state["ejecting"] and self.coolingStartTime != None and self.state["coolingTimeLeft"] > 0):
            # time remaining = total time - (current time - start time)
            self.state["coolingTimeLeft"] = self._settings.get(["coolingTime"]) - int(time.monotonic() - self.coolingStartTime)
        elif (self.state["coolingTimeLeft"] != None or self.coolingStartTime != None):
            self.state["coolingTimeLeft"] = None
            self.coolingStartTime = None

        return flask.jsonify(self.state)

    def is_api_adminonly(self):
        return True

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
__plugin_name__ = "Ejector"

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
