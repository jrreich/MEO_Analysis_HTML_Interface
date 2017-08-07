function submitpress() {
  if (document.getElementById('MEO').checked == true)
    {
      alert('HI checked')
    }
  else {
      alert('not checked')
  }
}

$("#siteIDinput").blur(function() {
    var SiteNum = $("#siteIDinput").val();
    $.getJSON('/api/sites/' + SiteNum, {}, function (data) {
		$('#StartTime').val(data.OpenTime)
        var items = [];
        $.each( data, function ( key, val) {
            items.push ( key + " - " + val);
        });
        /*$('#userbeaconid').prop('checked','true')*/
        $('#beaconIDinput').val(data.BcnId15)
		console.log(data);
    });
});

function renderHTML(data) {
alert(data['BcnId15'])

}

