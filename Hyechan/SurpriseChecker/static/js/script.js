d3.select("#mc")
    .on("mouseover", function(){showDropdown(this.id);})
    .on("mouseout", function(){hideDropdown(this.id);})

function showDropdown(myID) {
    d3.select("#" + myID)
    .selectAll("div")
        .style("visibility", "visible");
}

function hideDropdown(myID) {
    d3.select("#" + myID)
    .selectAll("div")
        .style("visibility", "hidden");
}