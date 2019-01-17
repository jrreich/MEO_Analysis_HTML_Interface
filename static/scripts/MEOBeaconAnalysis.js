$(function () {
    function submitpress() {
        if (document.getElementById('MEO').checked == true) {
            alert('HI checked')
        }
        else {
            alert('not checked')
        }
    }

    $("#siteIDinput").blur(function () {
        var SiteNum = $("#siteIDinput").val();
        $.getJSON('/api/sitesum/' + SiteNum, {}, function (data) {
            var sd = new Date(data.OpenTime);
            var ed = new Date(data.TimeLast);
            $('#beaconIDinput').val(data.BcnId15);
            $('#StartTime').val(sd.toISOString().slice(0, 16));
            $('#pasttime').prop('checked', true);
            $('#usersiteid').prop('checked', true);
            if (data.Closed == "Y") {
                $('#EndTime').val(ed.toISOString().slice(0, 16));
            };

        });
            


            /*$('#userbeaconid').prop('checked','true')*/

    });


    var eventlist = [
        {
            name: 'Lake George - Config # 1 - Slow speed - Boat',
            timeStart: '2017-07-20T15:10',
            timeEnd: '2017-07-20T19:09',
            bcnId: '279C753BAEFFBFF',
            usefile: 'true',
            filename: 'var/uploads/LakeGeorge_GT_all.csv'
        },
        {
            name: 'Lake George - Config # 2 - High speed - Hand',
            timeStart: '2017-07-20T20:04',
            timeEnd: '2017-07-20T20:22',
            usefile: 'true',
            bcnId: '279C753BAEFFBFF'
        },
        {
            name: 'Lake George - Config # 3 - Bobbing Dock',
            timeStart: '2017-07-20T20:38',
            timeEnd: '2017-07-20T22:00',
            useGT: 'true',
            lat: 43.49272,
            lon: -73.63208,
            bcnId: '279C753BAEFFBFF'
        },
        {
            name: 'Lake George - Config # 4 - Bobbing Morring',
            timeStart: '2017-07-20T22:01',
            timeEnd: '2017-07-21T12:23',
            useGT: 'true',
            lat: 43.49282,
            lon: -73.63268,
            bcnId: '279C753BAEFFBFF'
        },
        {
            name: 'Lake George - Config # 5 - Slow speed - Hand',
            timeStart: '2017-07-21T12:24',
            timeEnd: '2017-07-21T13:02',
            usefile: 'true',
            bcnId: '279C753BAEFFBFF'
        },
        {
            name: 'Lake George - Config # 6 - Hike',
            timeStart: '2017-07-21T13:25',
            timeEnd: '2017-07-21T17:09',
            usefile: 'true',
            bcnId: '279C753BAEFFBFF'
        },
        {
            name: 'Lake George - Config # 7 - Fixed Dock',
            timeStart: '2017-07-21T17:15',
            timeEnd: '2017-07-21T22:00',
            useGT: 'true',
            lat: 43.49272,
            lon: -73.63208,
            bcnId: '279C753BAEFFBFF'
        }
    ];



    window.onload = function () {
        var changeTime = function (time) {
            document.getElementById('startTime').value = time;
        };
        var changeAttr = function (field, value) {
            //alert(field + value);
            document.getElementById(field).value = value;
            //alert(field)
        };
        var eventsInt = document.getElementById('addEvents').onclick = function () {
            for (let i = 0; i < eventlist.length; i++) {
                r = $('<input>').attr({
                    type: 'button',
                    id: 'event' + i,
                    value: eventlist[i].name
                })
                    .click(function () {
                        $('#pasttime').attr('checked', true);
                        $('#userbeaconid').attr('checked', true);
                        if (eventlist[i].usefile == 'true') {
                            $('#gtfile').prop('checked', true);
                        };
                        if (eventlist[i].useGT == 'true') {
                            $('#gtlatlon').prop('checked', true);
                            changeAttr('latinput', eventlist[i].lat);
                            changeAttr('loninput', eventlist[i].lon);
                        };
                        changeAttr('StartTime', eventlist[i].timeStart);
                        changeAttr('EndTime', eventlist[i].timeEnd);
                        changeAttr('beaconIDinput', eventlist[i].bcnId);
                        changeAttr('beaconIDinputname', eventlist[i].name);


                    });
                $("#events").append(r);


            }
        };


    };


})
    

