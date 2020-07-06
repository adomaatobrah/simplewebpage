let text = ""
let mask = ""

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

function bold(elem) {
    d3.select(elem)
    .style("font-weight", "bold")
}

function unbold(elem) {
    d3.select(elem)
    .style("font-weight", "normal")
}

function checkAnswer(guess) {
    console.log(guess)
    console.log(mask)
    if (guess == mask) {
        d3.select(".results")
        .append("div")
            .text("Correct!")
    }
    else {
        d3.select(".results")
        .append("div")
            .text("Incorrect!")
    }
}

function basicDisplay(data) {
    let sentences = data.sentences;

    for (i = 0; i < sentences.length; i++) {
        d3.select("#list1")
        .append("li")
            .text(sentences[i])
            .on("click", function(){checkAnswer(this.innerHTML);})
            .on("mouseover", function(){bold(this);})
            .on("mouseout", function(){unbold(this);});
    }

    d3.select(".results")
    .append("div")
        .text("The model got: " + data.model_score)
        
    d3.select(".results")
    .append("div")
        .text("Wordfreq got: " + data.wordfreq_score)
}

function generateFITB() {
    textArr = text.split(mask);

    d3.select(".results")
    .text("")

    d3.select(".results")
    .append("span")
        .text(textArr[0])

    d3.select(".results")
    .append("span")
        .attr("id", "blank")
        .on("mouseover", function(){showDropdown(this.id);})
        .on("mouseout", function(){hideDropdown(this.id);})
        .text("__________")
        .append("div")
        .attr("class", "tooltiptext")
        .append("ol")
            .attr("id", "list1");
    
    d3.select(".results")
    .append("span")
        .text(textArr[1])

    d3.select("#list1")
    .append("li")
        .text(mask)
        .on("click", function(){checkAnswer(this.innerHTML);})
        .on("mouseover", function(){bold(this);})
        .on("mouseout", function(){unbold(this);});
}

// Receive data from user input fields
async function getData() {
    // Get the data from user input
    text = document.getElementById("text").value;
    console.log(text)
    mask = document.getElementById("mask").value;
    console.log(mask)

    var entry = {
        text: text,
        mask: mask
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

    generateFITB()
    basicDisplay(data)
}