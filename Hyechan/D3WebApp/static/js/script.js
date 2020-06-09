function showTooltip(myID) {
    d3.select("#" + myID)
        .selectAll("div")
            .style("visibility", "visible");
}

function hideTooltip(myID) {
    d3.select("#" + myID)
        .selectAll("div")
            .style("visibility", "hidden");
}