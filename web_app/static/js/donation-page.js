$(document).ready(function(){
    $('input[type=radio][name=btnradio]').change(function() {
        var value = this.value;
        var serviceChargeRate = $('#serviceChargeDiv :first-child').attr("data-service-charge-rate");
        var serviceCharge = value * serviceChargeRate

        $('#serviceChargeDiv').toggle();
        $('#totalDiv').toggle();
    });
});