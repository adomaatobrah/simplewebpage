<template>
  <div id="app">
    <h2>Text predictability</h2>
    <form action="/result" method="POST>
      <label for="usertext">Enter any text </label>
      <textarea id = "usertext" name='text'></textarea><br><br>
      <label for = "num">Predictions per word</label>
      <input type='text' name='number'><br><br>
      <input type='submit' value='Continue'>
    </form>
    <div class="results">
      Your input:
      <span class="tooltip" v-for="(word, ind) in inputdata.inputs" 
      v-bind:style="{ 'background-color': word[1] }">
       {{ word[0] }}
        <div v-if="ind != 0" id=ind class="tooltiptext">
          <ol>
            <li v-for="i in inputdata.predictions[ind-1]">
              <mark>
                '{{i}}'
              </mark>
            </li>
          </ol>
        </div>
      </span><br><br>
       <span style="background-color:lime;">Expected</span> (appeared in the first 10 predictions)<br>
       <span style="background-color:yellow;">Somewhat predictable</span> (appeared in the first 100 predictions)<br>
       <span style="background-color:red;">Somewhat unpredictable</span> (appeared in the first 1000 predictions)<br>
       <span style="background-color:magenta;">Unexpected</span> (didn't appear in the first 1000 predictions)<br><br>
    </div>
  </div>
</template>

<script>
import ToDo from './components/todo.vue';

export default {
  data() {
    return {
      greeting: 'Hello',
      inputdata: {"depth":5,
                  "final_score":0.6,
                  "inputs":[["It","white"],
                            [" is","lime"],
                            [" nice","red"],
                            [" to","lime"],
                            [" meet","lime"],
                            [" you","lime"]],
                  "len":5,
                  "positions":[0,null,0,null,0],
                  "predictions":[[" is","'s",",","."," was"],
                                [" not"," a"," important"," also"," the"],
                                [" to"," that"," and"," if",","],
                                [" see"," have"," know"," be"," hear"],
                                [" you"," with"," people"," a"," the"]],
                  "prompt":"It is nice to meet you",
                  "words":[" is"," nice"," to"," meet"," you"]}
    };
  },
  components: {
    ToDo,
  },
};
</script>

<style>
#app {
  font-family: Avenir, Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  text-align: center;
  color: #2c3e50;
  margin-top: 60px;
}
.results {
  text-align: left;
}

.tooltip {
  position: relative;
  display: inline-block;
}

.tooltip .tooltiptext {
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

.tooltip:hover .tooltiptext {
  visibility: visible;
}
</style>
