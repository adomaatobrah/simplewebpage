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

function basicDisplay(data) {
    d3.select(".results")
    .append("div")
        .text("The model got: " + data.model_score)
        
    d3.select(".results")
    .append("div")
        .text("Wordfreq got: " + data.wordfreq_score)
}

// Receive data from user input fields
async function getData() {
    // Get the data from user input
    let text = document.getElementById("text");
    let mask = document.getElementById("mask");

    var entry = {
        text: text.value,
        mask: mask.value
    };

    // Send the code to Flask
    let response = await fetch("http://127.0.0.1:5000/", {
        method: "POST",
        mode: "cors",
        body: JSON.stringify(entry),
        cache: "no-cache",
        headers: new Headers({
            "content-type": "application/json"
        })
    });

    // Get the data back from flask
    let data = await response.json()

    basicDisplay(data)
}