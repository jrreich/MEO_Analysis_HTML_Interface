
  var lutChart = dc.rowChart("#lutchart"), 
  satChart = dc.rowChart("#satchart"),
  missedPassPieChart = dc.pieChart('#missed-pass-pie-chart'),
  scheduledChart = dc.pieChart('#scheduled-pie-chart'),
  inspecChart = dc.pieChart('#inspec-pie-chart'),
  visCount = dc.dataCount(".dc-data-count"),
  visTable = dc.dataTable(".dc-data-table"),
  dailyPass = dc.barChart("#daily-pass-chart")

  // Look for the moveChart in https://dc-js.github.io/dc.js/stock.js to add Missed vs AOS or maybe a bubble of PDS size 
  
  formatDateTime = d3.timeFormat("%d-%b %Y %H:%M:%S")
  formatDay = d3.timeFormat("%d-%b %Y")

  //d3.csv('{{ json_data }}', function(err, data) {
  //    if (err) throw err;

  var dateFormatParser = d3.timeParse(formatDay);

  data1.forEach(function (d) {
    d.dd = d3.timeDay(new Date (d.aos));
    d.aos = formatDateTime(new Date(d.aos));
    d.los = formatDateTime(new Date(d.los));
    d.mccrcvd = (d.mccrcvd == null) ? null : formatDateTime( new Date(d.mccrcvd));
    d.timestamp = (d.timestamp == null) ? null : formatDateTime( new Date(d.timestamp));
    d.date = formatDay(new Date(d.aos));
    //d.dd = dateFormatParser(d.date);

  });
  

  
  var ndx = crossfilter(data1);
  var all = ndx.groupAll();



  var aosDim = ndx.dimension(function(d) {return d.aos});
  var azAosDim = ndx.dimension(function(d) {return d.azaos});
  var azLosDim = ndx.dimension(function(d) {return d.azlos});
  var azTcaDim = ndx.dimension(function(d) {return d.azTca});
  var conflictDim = ndx.dimension(function(d) {return d.conflict});
  var inspecDim = ndx.dimension(function(d) {return d.inspec});
  var losDim = ndx.dimension(function(d) {return d.los});
  var lutDim = ndx.dimension(function(d) {return d.lut});
  var maxelevationDim = ndx.dimension(function(d) {return d.maxelavation});
  var mccrcvdDim = ndx.dimension(function(d) {return d.mccrcvd});
  var missExcusedDim = ndx.dimension(function(d) {return d.missexcused});
  var missExcuseReasonDim = ndx.dimension(function(d) {return d.missexcusereason});
  var num406Dim = ndx.dimension(function(d) {return d.num406});
  var numintDim = ndx.dimension(function(d) {return d.numint});
  var orbitDim = ndx.dimension(function(d) {return d.orbit}); 
  var passMissedDim = ndx.dimension(function(d) {return d.passmissed});
  var passMissedReasonDim = ndx.dimension(function(d) {return d.passmissedreason});
  var passRcvdMccDim = ndx.dimension(function(d) {return d.passrcvdmcc});
  var passSummaryReceivedDim = ndx.dimension(function(d) {return d.passsummaryreceived});
  var satDim = ndx.dimension(function(d) {return d.sat});
  var scheduledDim = ndx.dimension(function(d) {return d.scheduled});
  var timeStampDim = ndx.dimension(function(d) {return d.timestamp});
  var dateDim = ndx.dimension(function(d) {return d.dd});
  var dayDim = ndx.dimension(function(d) {return d.dd});
  
  var aosGroup = aosDim.group() 
  var azAosGroup = azAosDim.group() 
  var azLosGroup = azLosDim.group() 
  var azTcaGroup = azTcaDim.group() 
  var conflictGroup = conflictDim.group() 
  var inspecGroup = inspecDim.group() 
  var losGroup = losDim.group() 
  var lutGroup = lutDim.group() 
  var maxelevationGroup = maxelevationDim.group()
  var mccrcvdGroup = mccrcvdDim.group() 
  var missExcusedGroup = missExcusedDim.group()
  var missExcuseReasonGroup = missExcuseReasonDim.group()
  var num406Group = num406Dim.group() 
  var numintGroup = numintDim.group() 
  var orbitGroup = orbitDim.group() 
  var passMissedGroup = passMissedDim.group() 
  var passMissedReasonGroup = passMissedReasonDim.group()
  var passRcvdMccGroup = passRcvdMccDim.group()
  var passSummaryReceivedGroup = passSummaryReceivedDim.group()
  var satGroup = satDim.group() 
  var scheduledGroup = scheduledDim.group()
  var timeStampGroup = timeStampDim.group()
  var dateGroup = dateDim.group().reduceCount();

  
  lutChart
    .width(250)
    .height(200)
    .margins({top: 10, right: 10, bottom: 10, left: 10})
    .dimension(lutDim)
    .group(lutGroup)
    .elasticX(true)
    .xAxis(d3.axisTop());

  satChart
    .width(250)
    .height(200)
    .margins({top: 10, right: 10, bottom: 10, left: 10})
    .dimension(satDim)
    .group(satGroup)
    .elasticX(true)
    .xAxis(d3.axisTop());
    
  missedPassPieChart
    .width(200)
    .height(200)
    .externalRadiusPadding(5)
    .dimension(passMissedDim)
    .group(passMissedGroup)
    .label(function (d) {
      if (missedPassPieChart.hasFilter() && !missedPassPieChart.hasFilter(d.key)) {
        return d.key + '(0%)';
      }
      var label = (d.key == true) ? "Missed " : "Successful ";
      if (all.value()) {
        label +='(' + (d.value / all.value() *100).toFixed(1) + '%)';
      }
      return label;
    });

  scheduledChart
    .width(200)
    .height(200)
    .externalRadiusPadding(5)
    .dimension(scheduledDim)
    .group(scheduledGroup)
    .label(function (d) {
      if (scheduledChart.hasFilter() && !scheduledChart.hasFilter(d.key)) {
        return d.key + '(0%)';
      }
      var label = (d.key == true) ? "Scheduled " : "Not ";
      if (all.value()) {
        label +='(' + (d.value / all.value() *100).toFixed(1) + '%)';
      }
      return label;
    });
    inspecChart
    .width(200)
    .height(200)
    .externalRadiusPadding(5)
    .dimension(inspecDim)
    .group(inspecGroup)
    .label(function (d) {
      if (inspecChart.hasFilter() && !inspecChart.hasFilter(d.key)) {
        return d.key + '(0%)';
      }
      var label = (d.key == true) ? "In Spec " : "Out of Spec ";
      if (all.value()) {
        label +='(' + (d.value / all.value() *100).toFixed(1) + '%)';
      }
      return label;
    });

  dailyPass
    .dimension(dateDim)
    .group(dateGroup)
    .width(1000)
    .elasticY(true)
    .gap(1)
    //.round(dc.round.floor)
    .x(d3.scaleTime().domain([minDate, maxDate]))
    .xUnits(d3.timeDays)
    .renderHorizontalGridLines(true)
    .renderTitle(true)
        .title(function (p) {
            return [
                p.key,
                p.value
            ].join('\n');
        })

  visCount
    .dimension(ndx)
    .group(all);

  visTable
    .dimension(aosDim)
    .group(function (d) {return formatDay(new Date(d.aos))}) //function (d) {
      //var format = d3.format('02d');
      //return d.aos.getFullYear() + '/' + format((d.aos.getMonth()+1));
      //(d.aos);
    //})
    .columns([
      {label: "LEOLUT", format: function(d) {return d.lut;}},
      "sat",
      "orbit",
      {label: "AOS", format: function(d) {return d.aos;}},
      {label: "LOS", format: function(d) {return d.los;}},
      "scheduled",
      "conflict",
      "inspec",
      "num406",
      "numint",
      {label: "Max Ele", format: function(d) {return d.maxelavation.toFixed(1);}},
      {label: "Az AOS", format: function(d) {return d.azaos.toFixed(1);}},
      {label: "Az LOS", format: function(d) {return d.azlos.toFixed(1);}},
      {label: "Az TCA", format: function(d) {return d.aztca.toFixed(1);}},
      {label: "Missed Pass", format: function(d) {return d.passmissed;}},
      {label: "Missed Pass Reason", format: function(d) {return d.passmissedreason;}},
      {label: "LEOLUT", format: function(d) {return d.passsummaryreceived;}},
      "mccrcvd"
    ]);
  
  dc.renderAll();
  

  