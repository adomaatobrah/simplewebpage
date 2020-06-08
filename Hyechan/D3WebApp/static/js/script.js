var tooltiptext = d3.select("#1")
    .style("position", "absolute")
    .style("visibility", "hidden"); 

d3.select("#tooltip1")
    .on("mouseover", function(){return tooltiptext.style("visibility", "visible");})
    .on("mouseout", function(){return tooltiptext.style("visibility", "hidden");});