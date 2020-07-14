<template>
    <html>
        <meta charset="utf-8">
            <body>
                <div class="center">
                    <h2 style = "text-align:center">Predicting words given full vs. no context</h2>
                    <div style = "text-align:center">
                        Text: <input type='text' id='text'><br><br>
                        <button id='submit' @click='getData();'>Continue</button>
                    </div>
                </div><br>

                <div class="key">
                    <span style="background-color:lime;">Easier with more context:</span> This word was far easier to predict with context<br>
                    <span style="background-color:red;">More context didn't change much:</span> Adding context did not make this word easier to predict<br>
                </div>

                <div id="resultsWrapper" class="results">
                    <div id="results"></div>
                    <br><br><br>
                    <div id="history">History: </div>
                    <div id="plot"></div>
                    <div id="guessplot"></div>
                    <div id="predstable"></div>
                </div>
            </body>
        </html>
</template>

<script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
<script src="./script.js"></script>
<script>
    export default {
        data() {
            return {
                input: {
                    text: ''
                },
                results: [],
                usedModels: []
            };
        },
        methods: {
            async getData() {
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

                generate(data, text.value);
            }
        }
    };
</script>

<style>
    .center {
    margin: auto;
    max-width: 800px;
    border: 3px solid black;
    padding: 10px;
    }

    .key {
    margin: auto;
    max-width: 800px;
    padding: 10px;
    }  

    .tooltip {
    position: relative;
    display: inline-block;
    }

    .tooltiptext {
    visibility: hidden;
    width: 150px;
    background-color: gray;
    color: #fff;
    text-align: left;
    padding: 5px 0;
    border-radius: 6px;
    font-size: 66.67%;

    position: absolute;
    z-index: 1;
    }

    .results {
    margin: auto;
    max-width: 800px;
    padding: 10px;
    }

    li:hover {
    font-weight: bold;
    }
</style>