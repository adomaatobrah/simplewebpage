<template>
  <div id="app">
    <h2>Text predictability</h2>
    <h2></h2>
    <div class="form-group">
      <label for="usertext">Enter any text </label>
      <textarea 
        id = "usertext" 
        name='text'
        v-model="input.text">
      </textarea><br><br>
      <label for = "num">Predictions per word </label>
      <input 
        type='text' 
        name='number'
        v-model="input.num"><br><br>
      <button @click="submit()">continue</button>
    </div>
    <div class="results">
      <br>
      Your input:
      <p style="font-size: 18px;">
      <span class="tooltip keep-spaces" v-for="(word, ind) in inputdata.inputs" 
       v-bind:style="{ 'background-color': word[1] }">
       {{word[0]}}
        <div v-if="ind != 0" id=ind class="tooltiptext">
          <ol>
            <li v-for="(i in inputdata.predictions[ind-1]">
              <button @click="recalculate(i, ind)">
                '{{i}}'
              </button>
            </li>
          </ol>
        </div>
      </span>
    </p>
      <br><br>
       <span style="background-color:lime;">Expected</span> (appeared in the first 10 predictions)<br>
       <span style="background-color:yellow;">Somewhat predictable</span> (appeared in the first 100 predictions)<br>
       <span style="background-color:red;">Somewhat unpredictable</span> (appeared in the first 1000 predictions)<br>
       <span style="background-color:magenta;">Unexpected</span> (didn't appear in the first 1000 predictions)<br><br>
      </div>
  </div>
</template>

<script>

export default {
  data() {
    return {
      inputdata: {"depth":0,
                  "final_score":0,
                  "inputs":[[],],
                  "len":0,
                  "positions":[],
                  "predictions":[[]],
                  "prompt":"",
                  "words":[]
                },
      input: {
        text: '',
        num: 5,
      },
      msg: ''
    };
  },


  methods: {
   async submit(){
    var url = new URL("http://localhost:5000/result"),
     params = {text:this.input.text, number:this.input.num}
     Object.keys(params).forEach(key => url.searchParams.append(key, params[key]))
     const res = await fetch(url);
     const input = await res.json();
     this.inputdata = input;
    },

    async recalculate(changedword, index){
     this.$set(this.inputdata.words, index, ' '.concat(changedword));
     var newinputstr = this.inputdata.words.join('');
     this.msg = newinputstr;

     var url = new URL("http://localhost:5000/result"),
     params = {text:newinputstr, number:this.input.num}
     Object.keys(params).forEach(key => url.searchParams.append(key, params[key]))
     const res = await fetch(url);
     const input = await res.json();
     this.inputdata = input;
    }
  }
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
  margin-left: 20%;
  margin-right: 20%
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

.keep-spaces { 
  white-space: pre-wrap; 
}
</style>
