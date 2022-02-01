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

        // TODO: controlViewModel might not be needed, maybe remove
        self.controlViewModel = parameters[0];

        self.onAfterBinding = () => {
            let controlContainer = $('#control-jog-general');
            let chainProductionControls = $('#controls_prusa_chain_production');

            chainProductionControls.insertAfter(controlContainer);
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
            }).done((data) => {
            }).always(() => {
            });
        }

        self.onReset = () => {
            self.executeCommand("reset");
        }

        self.onEject = () => {
            self.executeCommand("eject");
        }

        self.onSetFan = (_, e) => {
            const param = $(e.target).data('parameter');
            self.executeCommand("setFan", { enabled: param });
        }

        self.onSetLed = (_, e) => {
            const param = $(e.target).data('parameter');
            self.executeCommand("setLed", { enabled: param });
        }
    }

    /* view model class, parameters for constructor, container to bind to
     * Please see http://docs.octoprint.org/en/master/plugins/viewmodels.html#registering-custom-viewmodels for more details
     * and a full list of the available options.
     */
    OCTOPRINT_VIEWMODELS.push({
        construct: PrusaChainProductionViewModel,
        // ViewModels your plugin depends on, e.g. loginStateViewModel, settingsViewModel, ...
        dependencies: ['controlViewModel'],
        elements: ['#controls_prusa_chain_production']
    });
});
