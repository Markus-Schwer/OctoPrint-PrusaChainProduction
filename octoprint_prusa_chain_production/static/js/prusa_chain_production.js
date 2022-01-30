/*
 * View model for OctoPrint-PrusaChainProduction
 *
 * Author: Markus Schwer
 * License: AGPLv3
 */
$(() => {
    function PrusaChainProductionViewModel(parameters) {
        var self = this;

        // TODO: controlViewModel might not be needed, maybe remove
        self.controlViewModel = parameters[0];
        console.log("HELP");

        self.onAfterBinding = () => {
            let controlContainer = $('#control-jog-general');
            let chainProductionControls = $('#controls_prusa_chain_production');

            chainProductionControls.insertAfter(controlContainer);
            // only display the container after it was moved to the correct position
            chainProductionControls.css('display', '');
        };
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
