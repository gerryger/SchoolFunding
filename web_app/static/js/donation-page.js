$(document).ready(function(){
    $('input[type=radio][name=btnradio]').change(function() {
        var value = parseInt($(this).val());
        var serviceChargeRate = $('#serviceChargeDiv :first-child').attr("data-service-charge-rate");
        var serviceCharge = value * serviceChargeRate

        $('#serviceChargeDiv :nth-child(2)').text("$"+serviceCharge);

        var totalPrice = serviceCharge + value;
        $('#totalDiv :nth-child(2)').text("$"+totalPrice);

        $('#serviceChargeDiv').show();
        $('#totalDiv').show();
    });
});