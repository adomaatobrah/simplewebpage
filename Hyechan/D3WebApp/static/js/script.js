/* Global vars */
var userInput = ""
var userNum = 0

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

/* changeWord changes a part of the user input by replacing
 *      it with a prediction
 * Parameters:  pos, the position of the word to replace
 *              text, the text to replace it with
 *              rank, the topk() rank of text
 * Postcondition: the word at pos is altered to text, and its
 *      background color is updated according to rank
 */
async function changeWord(pos, origWord, text, rank) {
    d3.select("#tooltip" + pos + " > text").text(text);
    var wordToChange = d3.select("#tooltip" + pos);
    if (rank < 10) {
        wordToChange.style("background-color", "lime");
    }
    else if (rank < 100) {
        wordToChange.style("background-color", "yellow");
    }
    else if (rank < 1000) {
        wordToChange.style("background-color", "red");
    }
    else {
        wordToChange.style("background-color", "magenta");
    }

    userInput = userInput.replace(/ /g, "\u00a0");
    userInput = userInput.replace(origWord, text);
    userInput = userInput.replace(/\u00a0/g, " ");

    var entry = {
        text: userInput,
        num: userNum
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

    // Generate the color-coded text with that data
    generate(data);
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

/* generate() generates color-coded text from user input
 * Parameters: data, a JSON object containing all the necessary
 *          data to fill out the color-coded text
 * Postcondition: the page updates with color-coded text
 */
function generate(data) {
    // A list containing the words of user input, where
    //      each item is a word:color pair
    let inputList = data.inputs;
    // A list of lists of predicted words associated with each word
    //      of the input
    let predictionList = data.predictions;
    // The number of predictions to find
    let searchDepth = data.depth;
    // The final average predictability score
    let finalScore = data.final_score;
    // A list containing the positions in topk() where words
    //      of input were found (if any)
    let positionList = data.positions;
       
    // Clear the element with a .results class and append
    //      new text
    d3.select(".results").html("")
    .append("strong")
        .attr("id", "resultText")
        .text("Your input:")
    
    // Add a line break
    d3.select(".results")
    .append("br")

    // For each word in the input
    for (i = 0; i < inputList.length; i++) {
        // Extract the current word, color, and save the current position
        let currentWord = inputList[i][0].replace(" ", "\u00a0");
        let color = inputList[i][1];
        let wordPos = i;
        
        // Append the word with the appropriate text and color, and
        //      give it the show/hideTooltip functions
        d3.select(".results")
        .append("mark")
            .attr("id", "tooltip" + wordPos)
            .attr("class", "tooltip")
            .style("background-color", color)
            .style("font-size", "150%")
            .on("mouseover", function(){showTooltip(this.id);})
            .on("mouseout", function(){hideTooltip(this.id);})
            .append("text")
                .text(currentWord);
        
        // if not the first word (which was not predicted)
        if (wordPos != 0) {
            // Create a list element of predicted words to display
            d3.select("#tooltip" + wordPos)
            .append("div")
                .attr("id", "tooltiptext" + wordPos)
                .attr("class", "tooltiptext")
                .append("ol")
                    .attr("id", "list" + wordPos);
            
            // for each prediction made
            for (j = 0; j < searchDepth; j++) {
                // Force preserve spaces
                let word = predictionList[wordPos - 1][j].replace(" ", "\u00a0");
                // Save the current rank of the prediction
                let num = j
                // If the rank was in the position list
                if (num == positionList[wordPos - 1]) {
                    // Append a list item that is highlighted
                    d3.select("#list" + wordPos)
                    .append("li")
                        .on("click", function(){changeWord(wordPos, currentWord, word, num)})
                        .on("mouseover", function(){bold(this);})
                        .on("mouseout", function(){unbold(this);})
                        .append("mark")
                            .append("text")
                                .text(word);
                }
                else {
                    // Append a list item that is not highlighted
                    d3.select("#list" + wordPos)
                    .append("li")
                        .on("click", function(){changeWord(wordPos, currentWord, word, num)})
                        .on("mouseover", function(){bold(this);})
                        .on("mouseout", function(){unbold(this);})
                        .append("text")
                            .text(word)
                }
            }
        }
    }

    // Add line breaks
    d3.select(".results")
    .append("br")
    d3.select(".results")
    .append("br")

    // Append average predictability score
    d3.select(".results")
        .append("strong")
            .text("The average predictability score for the top " + searchDepth + " results is: ");
    
    d3.select(".results")
        .append("span")
            .text(finalScore);
}

// Receive data from user input fields
async function getData() {
    // Get the data from user input
    let text = document.getElementById("text");
    let num = document.getElementById("number");

    var entry = {
        text: text.value,
        num: num.value
    };

    userInput = text.value;
    userNum = num.value;

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

    // Generate the color-coded text with that data
    generate(data);
}