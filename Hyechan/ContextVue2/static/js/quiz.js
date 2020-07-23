var globalIndex = -1;

var blank_question = new Vue({
    el: "#question",
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
                
                logData(history_log.history[globalIndex]);
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

function generate(data) {    
    let results = data.results;
    let origText = data.text;

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

    blank_question.correctAnswer = blankedWord;
    blank_question.blankIndex = blank;

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
            blank:  false
        };
        if (i === blank) {
            dict.word = "__________\u00a0";
            dict.blank = true;
        }
        else {
            dict.word = initialWords[i] + "\u00a0";
        }
        outputs.push(dict);
    }

    blank_question.output = outputs;

    let optionsList = nextPreds.filter(x => x.id === blank && x.model === "smallContext").map(x => x.word);
    if (!(optionsList.includes(blankedWord))) {
        optionsList[optionsList.length - 1] = blankedWord;
    }
    console.log(nextPreds)
    console.log(optionsList)

    let shuffledOptions = shuffle(optionsList);
    blank_question.shuffledPreds = shuffledOptions;
}

async function generateQuestion() {
    globalIndex++;
    
    let response = await fetch("http://127.0.0.1:5000/quiz", {
        method: "POST",
        mode: "cors",
        cache: "no-cache",
        headers: new Headers({
            "content-type": "application/json",
            "question": "true"
        })
    });

    let data = await response.json();

    generate(data);
}


async function logData(histDict) {
    let response = await fetch("http://127.0.0.1:5000/quiz", {
        method: "POST",
        mode: "cors",
        body: JSON.stringify(histDict),
        cache: "no-cache",
        headers: new Headers({
            "content-type": "application/json",
            "question": "false"
        })
    });
}