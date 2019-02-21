
  var lutChart = dc.barChart("#lutchart"), 
  refBeaconChart = dc.barChart('#refBeaconChart'),
  numLocVsDistanceChart = dc.barChart('#numLocVsDistanceChart'),
  // meanVsDistanceChart = dc.barChart('#meanVsDistanceChart'),
  // lessThan5kmChart = dc.barChart('#lessThan5kmChart')
  dateChart = dc.lineChart("#date-chart")
  visCount = dc.dataCount(".dc-data-count"),
  visTable = dc.dataTable(".dc-data-table"),


  // Look for the moveChart in https://dc-js.github.io/dc.js/stock.js to add Missed vs AOS or maybe a bubble of PDS size 
  
  formatDateTime = d3.timeFormat("%d-%b %Y %H:%M:%S")
  formatDay = d3.timeFormat("%d-%b %Y")

  //d3.csv('{{ json_data }}', function(err, data) {
  //    if (err) throw err;

  var dateFormatParser = d3.timeParse(formatDay);

  data1.forEach(function (d) {
    d.dd = d3.timeDay(new Date (d.addtime));
    d.addtime = formatDateTime(new Date(d.addtime));
    d.starttime = formatDateTime(new Date(d.starttime));
    d.endtime = formatDateTime(new Date(d.endtime));
    d.num_of_locations = +d.num_of_locations;
    d.mean = +d.mean;
    d.distance_to_ref_beacon = Math.round(+d.distance_to_ref_beacon/100)*100;
    //d.date = formatDay(new Date(d.aos));
    //d.dd = dateFormatParser(d.date);

  });
  

  
  var ndx = crossfilter(data1);
  var all = ndx.groupAll();



  var addTimeDim = ndx.dimension(function(d) {return d.addtime});
  var beaconIdDim = ndx.dimension(function(d) {return d.beaconid});
  var beaconLatDim = ndx.dimension(function(d) {return d.beaconlat});
  var beaconLonDim = ndx.dimension(function(d) {return d.beaconlon});
  var distanceToRefDim = ndx.dimension(function(d) {return d.distance_to_ref_beacon});
  var endTimeDim = ndx.dimension(function(d) {return d.endtime});
  var expectedLocDim = ndx.dimension(function(d) {return d.expected_locations});
  var meanDim = ndx.dimension(function(d) {return d.mean});
  var medianDim = ndx.dimension(function(d) {return d.median});
  var meolutIdDim = ndx.dimension(function(d) {return d.meolutid});
  var numLocDim = ndx.dimension(function(d) {return d.num_of_locations;});

  var numLocGroupSum = numLocDim.group().reduceSum(function (d) { return d.num_of_locations; });
  var numLocGroupCount = numLocDim.group().reduceCount(function (d) { return d.num_of_locations; });

  var numLT2kmDim = ndx.dimension(function(d) {return d.number_less_than_2km});
  var numLT5kmDim = ndx.dimension(function(d) {return d.number_less_than_5km});
  var numLT10kmDim = ndx.dimension(function(d) {return d.number_less_than_10km});
  var numLT20kmDim = ndx.dimension(function(d) {return d.number_less_than_20km});
  var p75Dim = ndx.dimension(function(d) {return d.p75});
  var p90Dim = ndx.dimension(function(d) {return d.p90});
  var p95Dim = ndx.dimension(function(d) {return d.p95});
  var perLT2kmDim = ndx.dimension(function(d) {return d.percent_less_than_2km});
  var perLT5kmDim = ndx.dimension(function(d) {return d.percent_less_than_5km});
  var perLT10kmDim = ndx.dimension(function(d) {return d.percent_less_than_10km});
  var perLT20kmDim = ndx.dimension(function(d) {return d.percent_less_than_20km});
  var refBeaconDim = ndx.dimension(function(d) {return d.refbeacon});
  var startTimeDim = ndx.dimension(function(d) {return d.starttime});
  
  var addTimeGroup = addTimeDim.group() 
  var beaconIdGroup = beaconIdDim.group() 
  var beaconLatGroup = beaconLatDim.group() 
  var beaconLonGroup = beaconLonDim.group() 
  var distanceToRefGroup = distanceToRefDim.group() 
  var endTimeGroup = endTimeDim.group() 
  var expectedLocGroup = expectedLocDim.group() 
  var meanGroup = meanDim.group().reduceSum(function(d) {return d.mean}) 
  var medianGroup = medianDim.group()
  var meolutIdGroup = meolutIdDim.group()
  var numLocGroup = numLocDim.group()
  var numLT2kmGroup = numLT2kmDim.group()
  var numLT5kmGroup = numLT5kmDim.group()
  var numLT10kmGroup = numLT10kmDim.group() 
  var numLT20kmGroup = numLT20kmDim.group() 
  var p75Group = p75Dim.group() 
  var p90Group = p90Dim.group() 
  var p95Group = p95Dim.group()
  var perLT2kmGroup = perLT2kmDim.group()
  var perLT5kmGroup = perLT5kmDim.group()
  var perLT10kmGroup = perLT20kmDim.group() 
  var perLT20kmGroup = perLT20kmDim.group()
  var refBeaconGroup = refBeaconDim.group()
  var startTimeGroup = startTimeDim.group().reduceCount();

  
  lutChart
    .width(250)
    .dimension(meolutIdDim)
    .group(meolutIdGroup)
    .x(d3.scaleBand())
    .xUnits(dc.units.ordinal);

  refBeaconChart
    .width(1100)
    .height(200)
    .dimension(refBeaconDim)
    .group(refBeaconGroup)
    .x(d3.scaleBand())
    .xUnits(dc.units.ordinal);
    
  numLocVsDistanceChart
    .width(400)
    .height(200)
    .dimension(distanceToRefDim)
    .group(numLocGroupSum)
    //.colors(d3.schemeRdYlGn[9]) //fix this 
    .x(d3.scaleLinear().domain([0,15000]))
    .xAxisLabel("distance (km)")  
    .xUnits(d3.timeDays)
    .elasticY(true);


  // meanVsDistanceChart
  //   .width(400)
  //   .height(200)
  //   .dimension(distanceToRefDim)
  //   .group(meanGroup)
  //   .x(d3.scaleLinear().domain([0,10000]))
  //   .xAxisLabel("distance (km)");

  // lessThan5kmChart
  //   .width(400)
  //   .height(200)
  //   .dimension(perLT5kmDim)
  //   .group(perLT5kmGroup)
  //   .x(d3.scaleBand())
  //   .xUnits(dc.units.ordinal);

  dateChart

    .width(1000)
    .elasticY(true)
     //.round(dc.round.floor)
    .x(d3.scaleTime().domain([minDate, maxDate]))
    .xUnits(d3.timeDays)
    .renderHorizontalGridLines(true)
    .dimension(numLocDim)
    .group(addTimeGroup),


    // dateChart

  //   .width(1000)
  //   .elasticY(true)
  //    //.round(dc.round.floor)
  //   .x(d3.scaleTime().domain([minDate, maxDate]))
  //   .xUnits(d3.timeDays)
  //   .renderHorizontalGridLines(true)
  //   .compose([
  //     dc.lineChart(dateChart)
  //       .dimension(numLocDim)
  //       .group(addTimeGroup),
  //     dc.lineChart(dateChart)
  //       .dimension(perLT10kmGroup)
  //       .group(addTimeGroup)
  //   ])
  //   .brushOn(true);

  visCount
    .dimension(ndx)
    .group(all);

  visTable
    .dimension(addTimeDim)
    .group(function (d) {return formatDay(new Date(d.addtime))}) //function (d) {
      //var format = d3.format('02d');
      //return d.aos.getFullYear() + '/' + format((d.aos.getMonth()+1));
      //(d.aos);
    //})
    // .columns([
    //   {label: "MEOLUT", format: function(d) {return d.meolutid;}},
    //   {label: "Add Time", format: function(d) {return d.addtime;}},
    //   {label: "Start Time", format: function(d) {return d.starttime;}},
    //   {label: "End Time", format: function(d) {return d.endtime;}},
    //   "refbeacon",
    //   {label: "Distance to Ref Beacon", format: function(d) {return d.distance_to_ref_beacon.toFixed(1);}},
    //   "beaconlat",
    //   "beaconlon",
    //   "expected_locations",
    //   "num_of_locations",
    //   "percent_locations",
    //   "mean",
    //   "median",
    //   "p75",
    //   "p90",
    //   "p95"
    // ]);
  
  dc.renderAll();
  

  