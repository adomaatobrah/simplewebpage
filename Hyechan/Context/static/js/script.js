/* showTooltip reveals a tooltip attached to an element
 * Parameters: myID, the ID of the element with a tooltip
 * Postcondition: the tooltip attached to that element
 *      is made visible
 */
function showTooltip(myID) {
    d3.select("#" + myID)
    .selectAll("div")
        .style("visibility", "visible");
}

/* hideTooltip hides a tooltip attached to an element
 * Parameters: myID, the ID of the element with a tooltip
 * Postcondition: the tooltip attached to that element
 *      is made hidden
 */
function hideTooltip(myID) {
    d3.select("#" + myID)
    .selectAll("div")
        .style("visibility", "hidden");
}

/* Makes an element's font bold
 * Parameters: elem, an element
 * Postcondition: elem's font-weight is set to bold
 */
function bold(elem) {
    d3.select(elem)
    .style("font-weight", "bold")
}

/* Makes an element's font normal
 * Parameters: elem, an element
 * Postcondition: elem's font-weight is set to normal
 */

function unbold(elem) {
    d3.select(elem)
    .style("font-weight", "normal")
}
function generate(data) {
    let results = data.results;
    let colors = assignColors(results)
    let highestRatio = 0
    let blank = 0

    d3.select(".results").html("")
    .append("div")
        .attr("id", "colored_output")

    for (i = 0; i < results.length; i++) {
        bigToNoRatio = results[i].bigContextLogProb - results[i].noContextLogProb
        if (bigToNoRatio > highestRatio) {
            highestRatio = bigToNoRatio
            blank = i
        }

        d3.select("#colored_output")
        .append("span")
            .attr("id", "tooltip" + i)
            .text(results[i].word)
            .attr("style", "background-color:" + colors[i] + ";font-size:150%;")
    }

    d3.select("#tooltip" + blank)
    .attr("style", "background-color:white;")
    .text("__________ ")
    .on("mouseover", function(){showTooltip(this.id);})
    .on("mouseout", function(){hideTooltip(this.id);})
    .append("div")
        .attr("id", "tooltiptext" + blank)
        .attr("class", "tooltiptext")
        .append("ol")
            .attr("id", "list" + blank);

    for (j = 0; j < results[blank].bigContextPreds.length; j++) {
        d3.select("#list" + blank)
        .append("li")
            .text(results[blank].bigContextPreds[j])
            .attr("style", "font-size:150%;")
            .on("mouseover", function(){bold(this);})
            .on("mouseout", function(){unbold(this);})
    }

    let plotData = [
        {
          x: results.map(x=>x.word),
          y: results.map(x=>x.bigContextLogProb - x.noContextLogProb),
          type: 'bar',
          name: 'ratio (big context - no context)'
        },
        // {
        //   x: results.map(x=>x.word),
        //   y: results.map(x=>x.bigContextLogProb - x.smallContextLogProb),
        //   type: 'bar',
        //   name: 'ratio (big context - small context)'
        // },
        {
            x: results.map(x=>x.word),
            y: results.map(x=>x.noContextLogProb),
            type: 'bar',
            name: 'word frequency (log scale)'
        }
      ];
      Plotly.newPlot('plot', plotData);
}

function assignColors(results) {
    let logRatios = results.map(x => x.bigContextLogProb - x.noContextLogProb);
    return logRatios.map(x => {
        if (x > 5) return 'lime';
        return 'red';
    })
}

async function getData() {
    let text = document.getElementById("text");

    var entry = {
        text: text.value,
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