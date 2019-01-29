
$(document).ready(function () {
    $('.hoursRadio').change(function () {
        //$("#rthoursinput").toggle();
        $("#pasttimeinput").toggle();
    });
    //Toggle on realtime pasttime inputs
    $('input[name = "RealPastTime"]:radio').change(function () {
        if ($('input#realtime').is(':checked')) {
            $('#rthoursinput').show('fast');
            $('.pasttimeinput').hide();
        }
        else {
            $('#rthoursinput').hide();
            $('.pasttimeinput').show('fast');
        }
    });
    //Toggle on Site ID, Beacon ID fields 
    $('input[name = "UseBeaconID"]:radio').change(function () {
        if ($('input#userbeaconid').is(':checked')) {
            $('.beaconinputfield').hide(0);
            $('.beaconfield').slideDown('fast');
            $('.posfield').slideDown('fast');
            
        } else if ($('input#usersiteid').is(':checked')) {
            $('.beaconinputfield').hide(0);
            $('.sitefield').slideDown('fast');
            $('.posfield').slideDown('fast');
        } else {
            $('.beaconinputfield').hide(0);
        }
    });
    //Toggle on file input
    $('.fileinputradio:radio').change(function () {
        if ($(".fileinputneeded").is(':checked')) {
            $("#fileinput").show('fast');
        } else {
            $("#fileinput").hide(0);
        }
    });

    //Toggle on Filter groups
    $('#filter1check').change(function () {
        $('.filter1group').toggle();
    });
    $('#filter2check').change(function () {
        $('.filter2group').toggle();
    });
    $('#filter3check').change(function () {
        $('.filter3group').toggle();
    });

    //Toggle on filter range val fields 
    $('.filter1s:radio').change(function () {
        if ($('#filter1ran').is(':checked')) {
            $('.filter1-val-group').hide(0);
            $('.filter1-range-group').slideDown('fast');
            $('.filter1-range-group').slideDown('fast');
        
        } else {
            $('.filter1-val-group').slideDown('fast');
            $('.filter1-range-group').hide(0);
            $('.filter1-range-group').hide(0);
        }
    });
    $('.filter2s:radio').change(function () {
        if ($('#filter2ran').is(':checked')) {
            $('.filter2-val-group').hide(0);
            $('.filter2-range-group').slideDown('fast');
            $('.filter2-range-group').slideDown('fast');
        
        } else {
            $('.filter2-val-group').slideDown('fast');
            $('.filter2-range-group').hide(0);
            $('.filter2-range-group').hide(0);
        }
    });
    $('.filter3s:radio').change(function () {
        if ($('#filter3ran').is(':checked')) {
            $('.filter3-val-group').hide(0);
            $('.filter3-range-group').slideDown('fast');
            $('.filter3-range-group').slideDown('fast');
        
        } else {
            $('.filter3-val-group').slideDown('fast');
            $('.filter3-range-group').hide(0);
            $('.filter3-range-group').hide(0);
        }
    });

    //Show Vary By selection
    $('#plotvary').change(function () {
        $('.plotvaryby-group').toggle();
    });

    //Show Jdata selection
    $('#Jdata').change(function () {
        if ($('#Jdata').is(':checked')) {
            $('.Jdata-group').slideDown('fast');
        } else {
            $('.Jdata-group').hide();
        }
    });



    $("#siteIDinput").blur(function () {
        var SiteNum = $("#siteIDinput").val();
        $.getJSON('/api/sitesum/' + SiteNum, {}, function (data) {
            var now = new Date();
            var sd = new Date(data.OpenTime);
            var ed = new Date(data.TimeLast);
            $('#beaconIDinput').show('fast');
            $('#beaconIDinput').val(data.BcnId15);
            $('#StartTime').val(sd.toISOString().slice(0, 16));
            $('#pasttime').prop('checked', true);
            $('.pasttimeinput').show('fast');
            $('#usersiteid').prop('checked', true);
            if (data.Closed == "Y") {
                $('#EndTime').val(ed.toISOString().slice(0, 16));
            }
            else {
                $('#EndTime').val(now.toISOString().slice(0, 16));
            };
            if (data.CompLat) {
                $('#beaconLat').val(data.CompLat);
                $('#beaconLon').val(data.CompLon);
            }
            $('#siteLocationName').val('Site - ' + SiteNum)
            

        });



        /*$('#userbeaconid').prop('checked','true')*/

    });
    
});