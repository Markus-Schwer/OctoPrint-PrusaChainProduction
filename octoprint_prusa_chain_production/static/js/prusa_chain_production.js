/*
 * View model for OctoPrint-PrusaChainProduction
 *
 * Author: Markus Schwer
 * License: AGPLv3
 */
$(() => {
    function PrusaChainProductionViewModel(parameters) {
        var self = this;

        const PLUGIN_ID = "prusa_chain_production";

        self.loginStateViewModel = parameters[0];
        self.settingsViewModel = parameters[1];
        self.controlViewModel = parameters[2];
        self.ejectState = ko.observable("STANDBY");
        self.fanState = ko.observable("OFF");
        self.ledState = ko.observable("OFF");

        self.onAfterBinding = () => {
            // control tab
            let controlContainer = $("#control-jog-general");
            let chainProductionControls = $("#controls_prusa_chain_production");

            chainProductionControls.insertAfter(controlContainer);

            self.fetchStatus();
        };

        self.onDataUpdaterPluginMessage = (plugin, data) => {
            if (plugin === PLUGIN_ID) {
                self.fetchStatus();
            }
        };

        self.fetchStatus = () => {
            $.ajax({
                url: API_BASEURL + "plugin/" + PLUGIN_ID,
                type: "GET",
                contentType: "application/json; charset=UTF-8"
            }).done((data) => {
                if (data?.ejecting !== undefined)
                    self.ejectState(data.ejecting ? "EJECTING" : "STANDBY");
                if (data?.fansOn !== undefined)
                    self.fanState(data.fansOn ? "ON" : "OFF");
                if (data?.ledsOn !== undefined)
                    self.ledState(data.ledsOn ? "ON" : "OFF");
            });
        };

        self.executeCommand = (command, params = {}) => {
            $.ajax({
                url: API_BASEURL + "plugin/" + PLUGIN_ID,
                type: "POST",
                dataType: "json",
                data: JSON.stringify({
                    command,
                    ...params
                }),
                contentType: "application/json; charset=UTF-8"
            }).always(() => self.fetchStatus());
        };

        self.onStopEject = () => {
            self.executeCommand("stop_eject");
        };

        self.onEject = () => {
            self.executeCommand("eject");
        };

        self.onSetFan = (_, e) => {
            const param = $(e.target).data("parameter");
            self.executeCommand("setFan", {enabled: param});
        };

        self.onSetLed = (_, e) => {
            const param = $(e.target).data("parameter");
            self.executeCommand("setLed", {enabled: param});
        };
    }

    /* view model class, parameters for constructor, container to bind to
     * Please see http://docs.octoprint.org/en/master/plugins/viewmodels.html#registering-custom-viewmodels for more details
     * and a full list of the available options.
     */
    OCTOPRINT_VIEWMODELS.push({
        construct: PrusaChainProductionViewModel,
        // ViewModels your plugin depends on, e.g. loginStateViewModel, settingsViewModel, ...
        dependencies: ["loginStateViewModel", "settingsViewModel", "controlViewModel"],
        elements: [
            "#controls_prusa_chain_production",
            "#sidebar_plugin_prusa_chain_production_wrapper"
        ]
    });
});
