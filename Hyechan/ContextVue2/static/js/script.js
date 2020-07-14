var colored_output = new Vue({
    el: "#colored-output",
    data: {
        output: [],
        shuffledPreds: [],
        correctAnswer: "",
        blankIndex: 0
    },
    methods: {
        checkAnswer: function (guess, guessIndex) {
            if (guess === this.correctAnswer) {
                the_blank = this.output[this.blankIndex];
                the_blank.word = this.correctAnswer + "\u00a0";
                the_blank.blank = false;
            }
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
    console.log(results)
    preds_table.rows = results;
    preds_table.cols = Object.keys(results[0]);

    let origResults = results.filter(x => x.src === "original");
    console.log(origResults)
    let nextPreds = results.filter(x => x.src === "smallContext");
    console.log(nextPreds)

    // Get the words of the initial input
    let initialWords = origResults.filter(x => x.model === "smallContext").map(x => x.word);

    // Get the large context & no context log probabilities
    let bigContextProbs = origResults.filter(x => x.model === "bigContext").map(x => x.score);
    console.log(bigContextProbs)
    let noContextProbs = origResults.filter(x => x.model === "noContext").map(x => x.score);
    console.log(noContextProbs)

    // Compute log ratios
    let logRatios = [];
    for (i = 0; i < bigContextProbs.length; i++) {
        logRatios.push(bigContextProbs[i] - noContextProbs[i]);
    }
    console.log(logRatios)

    // create color array to assign colors
    let colors = assignColors(logRatios);

    // Variables needed to generate blanks
    let highestRatio = 0;
    let blank = 0;
    let blankedWord = "";

    for (i = 0; i < logRatios.length; i++) {
        word = initialWords[i];
        console.log(word);
        if (logRatios[i] > highestRatio) {
            highestRatio = logRatios[i];
            blank = i;
            blankedWord = word;
        }
    }

    colored_output.correctAnswer = blankedWord;
    colored_output.blankIndex = blank;

    let outputs = [];
    for (i = 0; i < logRatios.length; i++) {
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
    console.log(optionsList)

    let shuffledOptions = shuffle(optionsList);
    colored_output.shuffledPreds = shuffledOptions;

    let plotData = [
        {
          x: initialWords,
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
            x: initialWords,
            y: origResults.filter(x => x.model = "noContext").map(x=>x.score),
            type: 'bar',
            name: 'word frequency (log scale)'
        }
      ];
      Plotly.newPlot('plot', plotData);
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

    let data = await response.json();
    console.log(data)

    generate(data, text.value);
}