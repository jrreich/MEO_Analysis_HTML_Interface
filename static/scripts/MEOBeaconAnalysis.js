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
    SiteData = $.getJSON('/api/sites/' + SiteNum);
    /*var SiteRequest = new XMLHttpRequest();
    SiteRequest.open('GET', '/api/sites/'+ SiteNum);

    SiteRequest.open('GET', 'https://learnwebcode.github.io/json-example/animals-1.json'); */
    /*SiteRequest.onload = function() {
        var SiteData = JSON.parse(SiteRequest.responseText);
        console.log(SiteData[0]);
        renderHTML(SiteData[0]); 
    };

    SiteRequest.send()
    renderHTML(SiteData);*/
});

function renderHTML(data) {
alert(data)

}

