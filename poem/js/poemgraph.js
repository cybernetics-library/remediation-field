var poemgraph = {};


poemgraph.graphDataFromRawData = function(rawdata, bookdata) {

  var graph = {};

  //formatteddata = _.mapValues(_.groupBy(rawdata, 'memory_from'), function(d) { return _.map(d, 'memory_to'); })

  var rawlinks = _.concat(
      _.map(vueapp.rawdata, function(d) {
                 return { 'source': d.memory_from, 'target': d.book_id };
            }),
        _.map(vueapp.rawdata, function(d) {
                   return { 'source': d.book_id, 'target': d.memory_to };
              })
  );
  graph.links = _.map(
    _.groupBy(rawlinks, function(d) {return d.source + d.target}),
    function(d) { 
        return _.assign(d[0], { 'value': d.length});
    })


  graph.nodes = _.map(_.uniq( _.concat(_.map(vueapp.rawdata, 'book_id'), _.map(vueapp.rawdata, 'memory_to'), _.map(vueapp.rawdata, 'memory_from'))), function(d) {
      return { 'id': d, 'name': d };
  });

  return graph;
}





poemgraph.makeGraph = function(rawdata, bookdata) {

  graph = poemgraph.graphDataFromRawData(rawdata, bookdata);

  d3.selectAll("#d3svg g").remove();
  var svg = d3.select("#d3svg"),
        width = +svg.attr("width"),
        height = +svg.attr("height");

  var color = d3.scaleOrdinal(d3.schemeCategory20);

  var simulation = d3.forceSimulation()
      .force("link", d3.forceLink().id(function(d) { return d.id; }))
      .force("charge", d3.forceManyBody())
      .force("center", d3.forceCenter(width / 2, height / 2));


      var link = svg.append("g")
          .attr("class", "links")
          .selectAll("line")
          .data(graph.links)
          .enter().append("line")
          .attr("stroke-width", function(d) { return Math.sqrt(d.value); });
    
      var node = svg.append("g")
          .attr("class", "nodes")
          .selectAll("circle")
          .data(graph.nodes)
          .enter().append("g")
          .attr("class","node")
          .call(d3.drag()
                      .on("start", dragstarted)
                      .on("drag", dragged)
                      .on("end", dragended));

      node.append('circle')
          .attr("r", 50)
//          .attr("fill", function(d) { return color(d.group); })
    
      node.append("text")
        .attr("dx", 12)
        .attr("dy", ".35em")

          .text(function(d) { return d.name; });


    
      simulation
          .nodes(graph.nodes)
          .on("tick", ticked);
    
      simulation.force("link")
          .links(graph.links);
    
      function ticked() {
            link
                .attr("x1", function(d) { return d.source.x; })
                .attr("y1", function(d) { return d.source.y; })
                .attr("x2", function(d) { return d.target.x; })
                .attr("y2", function(d) { return d.target.y; });
        
            //node
                //.attr("cx", function(d) { return d.x; })
                //.attr("cy", function(d) { return d.y; });

            node.attr("transform", function(d, i) {     
                    return "translate(" + d.x + "," + d.y + ")"; 
                });
          }

  function dragstarted(d) {
      if (!d3.event.active) simulation.alphaTarget(0.3).restart();
      d.fx = d.x;
      d.fy = d.y;
  }

  function dragged(d) {
      d.fx = d3.event.x;
      d.fy = d3.event.y;
  }

  function dragended(d) {
      if (!d3.event.active) simulation.alphaTarget(0);
      d.fx = null;
      d.fy = null;
  }

}
