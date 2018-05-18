$(function () {
    $("#siteIDinput").blur(function () {
        var SiteNum = $("#siteIDinput").val();
        $.getJSON('/api/sitesum/' + SiteNum, {}, function (data) {
            var sd = new Date(data.OpenTime);
            var ed = new Date(data.TimeLast);
            $('#StartTime').val(sd.toISOString().slice(0, 16));
            $('#EndTime').val(ed.toISOString().slice(0, 16));


            /*$('#userbeaconid').prop('checked','true')*/
            $('#beaconIDinput').val(data.BcnId15);
           
        });
    });

    window.onload = function () {
        var changeTime = function (time) {
            document.getElementById('startTime').value = time;
        };
        var changeAttr = function (field, value) {
            //alert(field + value);
            document.getElementById(field).value = value;
            //alert(field)
        };
    };
})

    

