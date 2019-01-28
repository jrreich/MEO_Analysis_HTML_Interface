$(document).ready(function () {
    $('.hoursRadio').change(function () {
        //$("#rthoursinput").toggle();
        $("#pasttimeinput").toggle();
    });
    //Toggle on realtime pasttime inputs
    $('input[name = "RealPastTime"]:radio').change(function () {
        if ($('input#realtime').is(':checked')) {
            $('#rthoursinput').show('slow');
            $('.pasttimeinput').hide();
        }
        else {
            $('#rthoursinput').hide();
            $('.pasttimeinput').show('slow');
        }
    });
    //Toggle on Site ID, Beacon ID fields 
    $('input[name = "UseBeaconID"]:radio').change(function () {
        if ($('input#userbeaconid').is(':checked')) {
            $('.beaconinputfield').hide(0);
            $('.beaconfield').slideDown('slow');
            $('.posfield').slideDown('slow');
            
        } else if ($('input#usersiteid').is(':checked')) {
            $('.beaconinputfield').hide(0);
            $('.sitefield').slideDown('slow');
            $('.posfield').slideDown('slow');
        } else {
            $('.beaconinputfield').hide(0);
        }
    });
    //Toggle on file input
    $('.fileinputradio:radio').change(function () {
        if ($(".fileinputneeded").is(':checked')) {
            $("#fileinput").show('slow');
        } else {
            $("#fileinput").hide(0);
        }
    });
});