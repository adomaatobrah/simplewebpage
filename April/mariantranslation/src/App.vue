<template>
  <div id="app">
    <div class="form-group">
      <label for="userenglish">English text </label><br>
      <textarea 
        id = "userenglish" 
        name='text'
        v-model="input.english"
        rows="4" cols="50">
        It was a dark and stormy night.
      </textarea><br><br>
  
      <br> 
      <label for="firstword">Beginning of translation</label><br>
      <textarea 
        id = "firstword" 
        name='text'
        v-model="input.firstword"
        rows="4" cols="50"
        value="La">
      </textarea><br><br>
      <button @click="wholesentence(input.english, input.firstword)">continue</button>
  </div>
 
    <div class="results">
      Expected translation:
      <p style="font-size: 30px;">
        {{ wholeTranslation.expected }}
      </p>
      <br>
      Your translation:
      <p style="font-size: 30px;">
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
      <p style="font-size: 30px;">
        {{ wholeTranslation.newEnglish }}
      </p>
   </div>
  </div>
</template>

<script>

export default {
  data() {
    return {
      input: {
        english: '',
        firstword: '',
      },
      paraphrases: [],
      msg: '',
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

.tooltip:hover .tooltiptext {
  visibility: visible;
}

.keep-spaces { 
  white-space: pre-wrap; 
}
</style>
