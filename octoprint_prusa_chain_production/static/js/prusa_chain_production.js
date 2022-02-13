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
        self.printerStateViewModel = parameters[3];

        self.ejecting = ko.observable(undefined);
        self.fansOn = ko.observable(undefined);
        self.ledsOn = ko.observable(undefined);
        self.isErrorOrClosed = ko.observable(undefined);
        self.coolingTimeLeft = ko.observable(0);

        self.connectionButtonText = ko.pureComputed(() => {
            if (self.isErrorOrClosed()) return gettext("Connect");
            else return gettext("Disconnect");
        });
        self.ejectText = ko.pureComputed(() => {
            if (self.isErrorOrClosed()) return "-";
            else if (self.ejecting()) return gettext("EJECTING")
            else return gettext("IDLE");
        });
        self.fanText = ko.pureComputed(() => {
            if (self.isErrorOrClosed()) return "-";
            else if (self.fansOn()) return gettext("ON")
            else return gettext("OFF");
        });
        self.ledText = ko.pureComputed(() => {
            if (self.isErrorOrClosed()) return "-";
            else if (self.ledsOn()) return gettext("ON")
            else return gettext("OFF");
        });
        self.coolingTimeLeftText = ko.pureComputed(() => {
            if (!self.ejecting() && self.coolingTimeLeft() <= 0) return "-";
            else return formatDuration(self.coolingTimeLeft());
        });

        self.ejectEnabled = ko.pureComputed(() => {
            return !self.printerStateViewModel.isBusy() && !self.isErrorOrClosed() && !self.ejecting();
        });

        self.startCoolingCountdown = (countdownSeconds) => {
            clearInterval(self.countdown);
            self.coolingTimeLeft(countdownSeconds);

            self.countdown = setInterval(() => {
                const newTimeLeft = self.coolingTimeLeft() - 1;
                self.coolingTimeLeft(newTimeLeft);

                if (newTimeLeft <= 0) {
                    clearInterval(self.countdown);
                }
            }, 1000);
        };

        self.connect = () => {
            if (self.isErrorOrClosed()) self.executeCommand("connect");
            else self.executeCommand("disconnect");
        };

        self.onAfterBinding = () => {
            // control tab
            let controlContainer = $("#control-jog-general");
            let chainProductionControls = $("#controls_prusa_chain_production");

            chainProductionControls.insertAfter(controlContainer);

            self.fetchStatus();
        };

        self.onDataUpdaterPluginMessage = (plugin, data) => {
            // TODO: also update when print status changes
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
                self.isErrorOrClosed(data.errorOrClosed);
                self.ejecting(data.ejecting);
                self.fansOn(data.fansOn);
                self.ledsOn(data.ledsOn);
                if (data.coolingTimeLeft !== undefined) {
                    self.startCoolingCountdown(data.coolingTimeLeft);
                }
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
            }).done(() => self.fetchStatus());
        };

        self.onStopEject = () => {
            self.executeCommand("stop_eject");
        };

        self.onCoolAndEject = () => {
            self.executeCommand("coolAndEject");
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
        dependencies: ["loginStateViewModel", "settingsViewModel", "controlViewModel", "printerStateViewModel"],
        elements: [
            "#controls_prusa_chain_production",
            "#sidebar_plugin_prusa_chain_production_wrapper"
        ]
    });
});
