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

function generate(data) {
    let inputList = data.inputs;
    let predictionList = data.predictions;
    let searchDepth = data.depth;
    let finalScore = data.final_score;
    let positionList = data.positions;
        
    d3.select(".results").html("")
    .append("strong")
        .attr("id", "resultText")
        .text("Your input:")
        
    d3.select(".results")
    .append("br")

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

    d3.select(".results")
    .append("br")
    
    d3.select(".results")
    .append("br")

    d3.select(".results")
        .append("strong")
            .text("The predictability score for the top " + searchDepth + " results is: ")
    
    d3.select(".results")
        .append("span")
            .text(finalScore)
}

async function getData() {
    var text = document.getElementById("text");
    var num = document.getElementById("number");

    var entry = {
        text: text.value,
        num: num.value
    };

    let response = await fetch("http://127.0.0.1:5000/", {
        method: "POST",
        mode: "cors",
        body: JSON.stringify(entry),
        cache: "no-cache",
        headers: new Headers({
            "content-type": "application/json"
        })
    });

    let data = await response.json()

    generate(data);
}