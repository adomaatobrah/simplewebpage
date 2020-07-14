let globalIndex = 0;
let globalGuesses = 1;
let globalGuessArray = [];

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
    guess = elem.innerHTML;
    console.log(guess);
    console.log(answer);

    if (guess == answer) {
        d3.select("#info" + globalIndex)
        .text(" Total guesses: " + globalGuesses + ". Correct answer: " + answer);
        
        d3.select("#tooltip" + blankIndex)
        .text(answer + "\u00a0")
        .style("font-size", "150%");

        globalGuessArray.push({
            index: "Sentence " + globalIndex,
            guesses: globalGuesses
        });

        drawGuessPlot();

        globalGuesses = 1;
    }
    else {
        d3.select(elem)
        .style("color", "red");

        d3.select("#info" + globalIndex)
        .text(" Total guesses: " + globalGuesses);

        globalGuesses++;
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
    var currentIndex = anArray.length;

    while (0 != currentIndex) {
        let randomIndex = Math.floor(Math.random() * currentIndex);
        currentIndex -= 1;

        let temporaryValue = anArray[currentIndex];
        anArray[currentIndex] = anArray[randomIndex];
        anArray[randomIndex] = temporaryValue;
    }

    return anArray;
}

function generateTable(results) {
    debugger
    console.log(results)
    d3.select("#predstable")
    .html("")
    .append("table")
        .attr("id", "thetable")
        .append("thead")
            .attr("id", "header")
            .append("tr")
            .attr("id", "headerrow")
                .append("th")
                .text("Word");
    
    for (i = 0; i < results[0].usedModels.length; i++) {
        d3.select("#headerrow")
        .append("th")
            .text(results[0].usedModels[i]);
    }

    d3.select("#thetable")
    .append("tbody")
        .attr("id", "tablebody");

    for (i = 0; i < results.length; i++) {
        d3.select("#tablebody")
        .append("tr")
            .attr("id", "row" + i)
                .attr("style", "font-weight:bold;")
                .append("td")
                    .text(results[i].word);
        
        d3.select("#row" + i)
        .append("td")
            .text(results[i].bigContextLogProb);

        d3.select("#row" + i)
        .append("td")
            .text(results[i].smallContextLogProb);
    
        d3.select("#row" + i)
        .append("td")
            .text(results[i].noContextLogProb);

        for (j = 0; j < results[i].smallContextPreds.length; j++) {
            d3.select("#tablebody")
            .append("tr")
                .attr("id", "row" + i + "_" + j)
                .style("font-size", "75%")
                    .append("td")
                        .text(results[i].smallContextPreds[j]);
                        
            d3.select("#row" + i + "_" + j)
            .append("td")
                .text(results[i].bigPredsLogProbs[j]);

            d3.select("#row" + i + "_" + j)
            .append("td")
                .text(results[i].smallPredsLogProbs[j]);
                
            d3.select("#row" + i + "_" + j)
            .append("td")
                .text(results[i].noPredsLogProbs[j]);
        }
    }
}

function assignColors(logRatios) {
    return logRatios.map(x => {
        if (x > 5) return 'lime';
        return 'red';
    })
}

function generate(data, origText) {
    globalIndex++;
    console.log(data)
    
    let results = data.results;
    console.log(results)
    let origResults = results.filter(x => x.src === "original")
    console.log(origResults)
    let nextPreds = results.filter(x => x.src === "smallContext");
    console.log(nextPreds)

    let smallContextWords = origResults.filter(x => x.model === "smallContext");
    let bigContextProbs = origResults.filter(x => x.model === "bigContext").map(x => x.score);
    console.log(bigContextProbs)
    let noContextProbs = origResults.filter(x => x.model === "noContext").map(x => x.score);
    console.log(noContextProbs)
    let logRatios = [];
    for (i = 0; i < bigContextProbs.length; i++) {
        logRatios.push(bigContextProbs[i] - noContextProbs[i]);
    }
    console.log(logRatios)

    let colors = assignColors(logRatios);
    let highestRatio = 0;
    let blank = 0;
    let blankedWord = "";

    d3.select("#results").html("")
    .append("div")
        .attr("id", "colored_output");

    for (i = 0; i < logRatios.length; i++) {
        word = smallContextWords[i].word;
        console.log(word);
        if (logRatios[i] > highestRatio) {
            highestRatio = logRatios[i];
            blank = i;
            blankedWord = word;
        }

        d3.select("#colored_output")
        .append("span")
            .attr("id", "tooltip" + i)
            .attr("class", "tooltip")
            .text(word + "\u00a0")
            .attr("style", "background-color:" + colors[i] + ";font-size:150%;");
    }

    origText = origText.replace(blankedWord, "_________");
    d3.select("#history")
    .append("div")
        .attr("id", "sentence" + globalIndex)
        .text("Sentence " + (globalIndex) + ": " + origText)
        .append("span")
            .attr("id", "info" + globalIndex)
            .text(" Total guesses: ");

    addBlank(blank);

    let optionsList = nextPreds.filter(x => x.id === blank && x.model === "smallContext").map(x => x.word);
    if (!(optionsList.includes(blankedWord))) {
        optionsList[optionsList.length - 1] = blankedWord;
    }
    console.log(optionsList)

    let shuffledOptions = shuffle(optionsList);

    for (j = 0; j < shuffledOptions.length; j++) {
        d3.select("#list" + blank)
        .append("li")
            .attr("id", "listitem" + j)
            .text(shuffledOptions[j])
            .attr("style", "font-size:150%;")
            .on("click", function(){checkAnswer(this, blankedWord, blank);});
    }

    let plotData = [
        {
        x: smallContextWords.map(x => x.word),
        y: logRatios,
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
            x: smallContextWords.map(x => x.word),
            y: origResults.filter(x => x.model = "noContext").map(x=>x.score),
            type: 'bar',
            name: 'word frequency (log scale)'
        }
    ];
    Plotly.newPlot('plot', plotData);

    generateTable(results);
}