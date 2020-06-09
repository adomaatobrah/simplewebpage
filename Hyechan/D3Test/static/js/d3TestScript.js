var tooltip = d3.select("#tooltip")

d3.select("#myDiv")
    .on("mouseover", function(){return tooltip.style("visibility", "visible");})
    .on("mouseout", function(){return tooltip.style("visibility", "hidden");});