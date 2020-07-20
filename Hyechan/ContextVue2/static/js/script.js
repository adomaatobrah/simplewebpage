var globalIndex = -1;

var colored_output = new Vue({
    el: "#colored-output",
    data: {
        output: [],
        shuffledPreds: [],
        correctAnswer: "",
        blankIndex: 0
    },
    methods: {
        checkAnswer: function (guess, elem) {
            if (guess === this.correctAnswer) {
                let the_blank = this.output[this.blankIndex];
                the_blank.word = this.correctAnswer + "\u00a0";
                the_blank.blank = false;
                history_log.history[globalIndex].guesses++;
                history_log.history[globalIndex].complete = true;

                guess_plot.x.push("Sentence " + (globalIndex + 1));
                guess_plot.y.push(history_log.history[globalIndex].guesses);
                guess_plot.drawPlot();

                globalIndex++;
            }
            else {
                elem.style.color = "red"
                history_log.history[globalIndex].guesses++;
            }
        }
    }
})

var history_log = new Vue({
    el: "#history",
    data: {
        history: []
    }
})

var guess_plot = new Vue({
    el: "#guessplot",
    data: {
        x: [],
        y: []
    },
    methods: {
        drawPlot: function () {
            let plotData = [
                {
                    x: this.x,
                    y: this.y,
                    type: 'bar',
                    name: "Sentence guess count"
                }
            ]
            Plotly.newPlot("guessplot", plotData);
        }
    }
})

var preds_table = new Vue({
    el: "#preds-table",
    data: {
        rows: [],
        cols: []
    }
})

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

function assignColors(logRatios) {
    return logRatios.map(x => {
        if (x > 5) return 'lime';
        return 'red';
    })
}

function generate(data, origText) {    
    let results = data.results;
    preds_table.rows = results;
    preds_table.cols = Object.keys(results[0]);

    let origResults = results.filter(x => x.src === "original");
    let nextPreds = results.filter(x => x.src === "smallContext");

    // Get the words of the initial input
    let initialWords = origResults.filter(x => x.model === "smallContext").map(x => x.word);

    // Get the large context & no context log probabilities
    let bigContextProbs = origResults.filter(x => x.model === "bigContext").map(x => x.score);
    let smallContextProbs = origResults.filter(x => x.model === "smallContext").map(x => x.score);
    let noContextProbs = origResults.filter(x => x.model === "noContext").map(x => x.score);

    // Compute log ratios
    let bigNoLogRatios = [];
    let bigSmallLogRatios = [];
    let smallNoLogRatios = [];
    for (i = 0; i < bigContextProbs.length; i++) {
        bigNoLogRatios.push(bigContextProbs[i] - noContextProbs[i]);
        bigSmallLogRatios.push(bigContextProbs[i] - smallContextProbs[i]);
        smallNoLogRatios.push(smallContextProbs[i] - noContextProbs[i]);
    }

    // create color array to assign colors
    let colors = assignColors(bigNoLogRatios);

    // Variables needed to generate blanks
    let highestRatio = 0;
    let blank = 0;
    let blankedWord = "";

    for (i = 0; i < bigNoLogRatios.length; i++) {
        word = initialWords[i];
        if (bigNoLogRatios[i] > highestRatio) {
            highestRatio = bigNoLogRatios[i];
            blank = i;
            blankedWord = word;
        }
    }

    colored_output.correctAnswer = blankedWord;
    colored_output.blankIndex = blank;

    let histText = origText.replace(blankedWord, "__________");
    var histEntry = {
        sentence: histText,
        answer: blankedWord,
        guesses: 0,
        complete: false
    }
    history_log.history.push(histEntry);

    let outputs = [];
    for (i = 0; i < bigNoLogRatios.length; i++) {
        var dict = {
            word: "",
            color: "",
            blank:  false
        };
        if (i === blank) {
            dict.word = "__________\u00a0";
            dict.color = "white";
            dict.blank = true;
        }
        else {
            dict.word = initialWords[i] + "\u00a0";
            dict.color = colors[i];
        }
        outputs.push(dict);
    }

    colored_output.output = outputs;

    let optionsList = nextPreds.filter(x => x.id === blank && x.model === "smallContext").map(x => x.word);
    if (!(optionsList.includes(blankedWord))) {
        optionsList[optionsList.length - 1] = blankedWord;
    }
    console.log(nextPreds)
    console.log(optionsList)

    let shuffledOptions = shuffle(optionsList);
    colored_output.shuffledPreds = shuffledOptions;

    let plotData = [
        {
          x: initialWords,
          y: bigNoLogRatios,
          type: 'bar',
          name: 'ratio (big context - no context)'
        },
        {
          x: initialWords,
          y: bigSmallLogRatios,
          type: 'bar',
          name: 'ratio (big context - small context)'
        },
        {
            x: initialWords,
            y: smallNoLogRatios,
            type: 'bar',
            name: 'ratio (small context - no context)'
        },
        {
            x: initialWords,
            y: bigContextProbs,
            type: 'bar',
            name: 'big model probs (log scale)'
        },
        {
            x: initialWords,
            y: smallContextProbs,
            type: 'bar',
            name: 'small model probs (log scale)'
        },
        {
            x: initialWords,
            y: noContextProbs,
            type: 'bar',
            name: 'word frequency (log scale)'
        }
    ];
    Plotly.newPlot('plot', plotData);
}

async function getData() {
    let text = document.getElementById("text");
    globalIndex++;

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

    let data = await response.json();

    generate(data, text.value);
}