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

function generate(inputList, predictionList, positionList, searchDepth) {
    for (i = 0; i < inputList.length; i++) {
        let currentWord = inputList[i][0].replace(" ", "\u00a0");
        let color = inputList[i][1];
        let wordPos = i;
        
        d3.select(".results")
            .append("mark")
                .attr("id", "tooltip" + wordPos)
                .attr("class", "tooltip")
                .style("background-color", color)
                .style("font-size", "150%")
                .text(currentWord)
                .on("mouseover", function(){showTooltip(this.id);})
                .on("mouseout", function(){hideTooltip(this.id);});
        
        if (wordPos != 0) {
            d3.select("#tooltip" + wordPos)
                .append("div")
                    .attr("id", "tooltiptext" + wordPos)
                    .attr("class", "tooltiptext")
                    .append("ol")
                        .attr("id", "list" + wordPos);
            
            for (j = 0; j < searchDepth; j++) {
                if (j == positionList[wordPos - 1]) {
                    d3.select("#list" + wordPos)
                        .append("li")
                            .append("mark")
                                .text(predictionList[wordPos - 1][j].replace(" ", "\u00a0"))
                }
                else {
                    d3.select("#list" + wordPos)
                        .append("li")
                            .text(predictionList[wordPos - 1][j].replace(" ", "\u00a0"))
                }
            }
        }
    }
}