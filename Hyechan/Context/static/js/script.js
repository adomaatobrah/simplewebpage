let globalIndex = 0
let globalGuesses = 1
let globalGuessArray = []

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

function drawGuessPlot() {
    let plotData = [
        {
            x: globalGuessArray.map(x=>x.index),
            y: globalGuessArray.map(x=>x.guesses),
            type: 'bar',
            name: 'number of guesses per sentence'
        }
    ];
    let layout = {
        title: 'Number of guesses per sentence',
        xaxis: {
          title: 'Sentence Number',
          showgrid: false,
          zeroline: false
        },
        yaxis: {
          title: 'Number of Guesses',
          showline: false
        }
    };
    Plotly.newPlot('guessplot', plotData, layout);
}

function checkAnswer(elem, answer, blankIndex) {
    guess = elem.innerHTML
    console.log(guess)
    console.log(answer)

    if (guess == answer) {
        d3.select("#info" + globalIndex)
        .text(" Total guesses: " + globalGuesses + ". Correct answer: " + answer)
        
        d3.select("#tooltip" + blankIndex)
        .text(answer + "\u00a0")
        .style("font-size", "150%")

        globalGuessArray.push({
            index: "Sentence " + globalIndex,
            guesses: globalGuesses
        })

        drawGuessPlot()

        globalGuesses = 1
    }
    else {
        d3.select(elem)
        .style("color", "red")

        d3.select("#info" + globalIndex)
        .text(" Total guesses: " + globalGuesses)

        globalGuesses++
    }
}

function addBlank(blank) {
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
}

function shuffle(anArray) {
    var currentIndex = anArray.length

    while (0 != currentIndex) {
        let randomIndex = Math.floor(Math.random() * currentIndex);
        currentIndex -= 1;

        let temporaryValue = anArray[currentIndex];
        anArray[currentIndex] = anArray[randomIndex];
        anArray[randomIndex] = temporaryValue;
    }

    return anArray;
}

function generate(data, origText) {
    globalIndex++
    
    let results = data.results;
    let colors = assignColors(results)
    let highestRatio = 0
    let blank = 0
    let blankedWord = ""

    d3.select("#results").html("")
    .append("div")
        .attr("id", "colored_output")

    for (i = 0; i < results.length; i++) {
        word = results[i].word
        console.log(word)
        bigToNoRatio = results[i].bigContextLogProb - results[i].noContextLogProb
        if (bigToNoRatio > highestRatio) {
            highestRatio = bigToNoRatio
            blank = i
            blankedWord = word
        }

        d3.select("#colored_output")
        .append("span")
            .attr("id", "tooltip" + i)
            .attr("class", "tooltip")
            .text(word + "\u00a0")
            .attr("style", "background-color:" + colors[i] + ";font-size:150%;")
    }

    origText = origText.replace(blankedWord, "_________")
    d3.select("#history")
    .append("div")
        .attr("id", "sentence" + globalIndex)
        .text("Sentence " + (globalIndex) + ": " + origText)
        .append("span")
            .attr("id", "info" + globalIndex)
            .text(" Total guesses: ")

    addBlank(blank)

    let optionsList = results[blank].bigContextPreds
    if (!(optionsList.includes(blankedWord))) {
        optionsList[optionsList.length - 1] = blankedWord
    }

    let shuffledOptions = shuffle(optionsList)

    for (j = 0; j < shuffledOptions.length; j++) {
        d3.select("#list" + blank)
        .append("li")
            .attr("id", "listitem" + j)
            .text(shuffledOptions[j])
            .attr("style", "font-size:150%;")
            .on("mouseover", function(){bold(this);})
            .on("mouseout", function(){unbold(this);})
            .on("click", function(){checkAnswer(this, results[blank].word, blank);})
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

    generate(data, text.value);
}