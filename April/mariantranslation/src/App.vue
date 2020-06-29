<template>
  <div id="app">
    <div class="form-group">
      <label for="userenglish">English text </label><br>
      <textarea 
        id = "userenglish" 
        name='text'
        v-model="input.english"
        rows="4" cols="50"
        required
        v-on:keyup="sParaphrases = [], eParaphrases = []">
        It was a dark and stormy night.
      </textarea><br><br>
  
      <br> 
      <br>
      <label for="firstword">Beginning of translation</label><br>
      <textarea 
        id = "firstword" 
        name='text'
        v-model="input.firstword"
        rows="4" cols="50"
        value="La"
        :disabled = checked>
      </textarea><br>
      <input type="checkbox" id="checkbox" v-model="checked">
      <label for="checkbox">Use default translation</label><br><br>
      <button @click="wholesentence(input.english, input.firstword)">continue</button>
  </div>
 
    <div class="results">
      Expected translation:
      <p style="font-size: 25px;">
        {{ wholeTranslation.expected }}
      </p>
      Your translation:
      <p style="font-size: 25px;">
      <span class="tooltip" v-for="(word, ind) in wholeTranslation.tokens">
        {{ word }}
        <div id=ind class="tooltiptext">
          <ol>
            <li v-for="(i in wholeTranslation.predictions[ind]">
              <button @click="recalculate(i, ind)">
                '{{i}}'
              </button>
            </li>
          </ol>
        </div>
      </span>
    </p>
      English:
      <p style="font-size: 25px;">
        {{ wholeTranslation.newEnglish }}
      </p>
      History:
      <div class="grid-container">
        <div class="grid-item">
          <p style="text-align:center">Spanish</p>
        <p v-for="paraphrase in sParaphrases">
          <button @click="wholesentence(input.english, paraphrase)" class="para">
            {{ paraphrase }}
          </button>
        </p>
      </div>
        <div class="grid-item">
          <p style="text-align:center">English</p>
        <p v-for="paraphrase in eParaphrases">
         <button class="para">
          {{ paraphrase }}
         </button>
        </p>
      </div>
      </div>

   </div>
  </div>
</template>

<script>
export default {
  data() {
    return {
      tab1: "true",
      tab2: "false",
      input: {
        english: '',
        firstword: '',
      },
      sParaphrases: [],
      eParaphrases: [],
      msg: '',
      checked: false,
      wholeTranslation: {"translation": '',
                         "expected": '',
                         "newEnglish": '',
                         "tokens": [],
                         "predictions" : []},
    };
  },

  methods: {
    async wholesentence(english, spanish){
     var url = new URL("http://localhost:5000/result"),
     params = {english:english, spanish:spanish}
     Object.keys(params).forEach(key => url.searchParams.append(key, params[key]))
     const res = await fetch(url);
     const input = await res.json();
     this.wholeTranslation = input;
     this.sParaphrases.unshift(this.wholeTranslation.translation)
     this.eParaphrases.unshift(this.wholeTranslation.newEnglish)
    },
    async recalculate(changedword, index){
     this.$set(this.wholeTranslation.tokens, index, changedword);
     var thelist = this.wholeTranslation.tokens.slice(0, index+1);
     var newinputstr = thelist.join('').replace(/\u00a0/g, ' ');
     this.wholesentence(this.input.english, newinputstr)
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
.tooltip:hover .tooltiptext { visibility: visible;}

button.para { background:none; border:none; text-align: left;}

button.para:hover { cursor: pointer;}

.grid-container {
  display: grid;
  grid-template-columns: auto auto auto;
  padding: 10px;
}
.grid-item {
  border: 1px solid rgba(0, 0, 0, 0.8);
  padding: 20px;
  font-size: 15px;
  text-align: left;
}
</style>
