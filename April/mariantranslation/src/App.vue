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
      <label for="start">Desired beginning</label><br>
      <textarea 
        id = "start" 
        name='text'
        v-model="input.start"
        rows="4" cols="50"
        value="La"
        :disabled = defaulttrans>
      </textarea><br>
      <input type="checkbox" id="default-checkbox" v-model="defaulttrans">
      <label for="checkbox">Use default translation</label><br><br>
      <input type="checkbox" id="auto-checkbox" v-model="auto">
      <label for="checkbox">Show auto-generated rewordings</label><br><br>
      <input type="checkbox" id="skip-checkbox" v-model="skip">
      <label for="checkbox">English only</label><br><br>
      <button @click="getResult(input.english, input.start)">continue</button>
  </div>
 
    <div v-if="!hideTranslation" class="results">
      Expected translation:<br><br>
      <button @click="auto = false; getResult(input.english, wholeTranslation.expected)" style="font-size: 25px;" class = "plain">
        {{ wholeTranslation.expected }}
      </button><br><br>
      Generated translation(s):<br>
      <p v-for="(alt, ind) in wholeTranslation.alternatives" class="tooltip">
        <button @click="auto = false; getResult(input.english, alt)" style="font-size: 25px;" class = "plain">
          {{ alt }}<br>
          <div class="tooltiptext" style="width: 90%">
            {{ wholeTranslation.engAlternatives[ind] }}
          </div>
        </button>
      </p>
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
      English back translation:
      <p style="font-size: 25px;">
        {{ wholeTranslation.newEnglish }}
      </p>
      History:
      <div class="grid-container">
        <div class="grid-item">
          <p style="text-align:center">Spanish</p>
        <p v-for="paraphrase in sParaphrases">
          <button @click="auto=false; getResult(input.english, paraphrase)" class="plain">
            {{ paraphrase }}
          </button>
        </p>
      </div>
        <div class="grid-item">
          <p style="text-align:center">English</p>
        <p v-for="paraphrase in eParaphrases">
         <button @click="skip=true; getResult(paraphrase, input.start)" class="plain">
          {{ paraphrase }}
         </button>
        </p>
      </div>
      </div>
   </div>

   <div v-if="!hideAlts" class="results">
    Alternatives:<br>
    <p v-for="(alt, ind) in wholeTranslation.alternatives" class="tooltip">
      <button @click="auto = false; getResult(input.english, alt)" style="font-size: 25px;" class = "plain">
        {{ alt }}
        <div class="tooltiptext" style="width: 90%">
          {{ wholeTranslation.engAlternatives[ind] }}
        </div>
      </button><br>
    </p>

    <p style="font-size: 25px;">
    <span class="tooltip" style="font-size: 25px;" 
            v-for="(word, ind) in wholeTranslation.tokens">
    <span @click="selected = word"
    :class="colorClass(word)"
    style = "cursor: pointer">
    {{ word }}
    </span> 
      <div id=ind class="tooltiptext">
        <ol>
          <li v-for="(i in wholeTranslation.predictions[ind]">
            <button @click="selected = ''; recalculate(i, ind)">
              '{{i}}'
            </button>
          </li>
        </ol>
      </div>
    </span>
    <button @click="getResult(input.english, selected)">
      Rearrange
    </button>
  </p>
    To move a word towards the front, select the token and click Rearrange. <br>
     <br><br>
    History:
      <p v-for="paraphrase in eParaphrases">
        <button @click="skip=true; getResult(paraphrase, input.start)" class="plain">
          {{ paraphrase }}
        </button>
      </p>
    </div>
 </div>
  </div>
</template>

<script>
export default {
  data() {
    return {
      input: {
        english: '',
        start: '',
      },
      sParaphrases: [],
      eParaphrases: [],
      msg: '',
      defaulttrans: false,
      auto: false,
      skip: false,
      hideTranslation: true,
      hideAlts: true,
      selected: '',
      wholeTranslation: {"translation": '',
                         "expected": '',
                         "newEnglish": '',
                         "tokens": [],
                         "predictions" : [],
                         "alternatives" : [],
                         "engAlternatives" : [],
                          }
    };
  },

  methods: {
    async getResult(english, start){
     if (this.auto){
       var url = new URL("http://localhost:5000/auto");
        }
     else if (this.selected != ''){
         var url = new URL("http://localhost:5000/rearrange");
       }
      else{
        var url = new URL("http://localhost:5000/result")
       }

    if (this.skip == true){ var skip = "true"}
    else{var skip = "false"}

    var params = {english:english, start:start, skip:skip}
    Object.keys(params).forEach(key => url.searchParams.append(key, params[key]))
    const res = await fetch(url);
    const input = await res.json();
    this.wholeTranslation = input;

    if (this.selected == ''){this.eParaphrases.unshift(this.wholeTranslation.newEnglish);}
    else{
      this.selected = '';
      this.getResult(this.wholeTranslation.newEnglish, '')
    }
    if (skip == "false"){
      this.hideTranslation = false;
      this.hideAlts = true;
      this.sParaphrases.unshift(this.wholeTranslation.translation);
    }
    else{
      this.hideAlts = false;
      this.hideTranslation = true;
    }
  },
    async recalculate(changedword, index){
     this.$set(this.wholeTranslation.tokens, index, changedword);
     var thelist = this.wholeTranslation.tokens.slice(0, index+1);
     var newinputstr = thelist.join('').replace(/\u00a0/g, ' ');
     this.getResult(this.input.english, newinputstr)
    },
    colorClass(word) {
      if (word==this.selected){
        return "blueClass";
      }
      else {return "tooltip"}
      }
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
.blueClass {
  background-color: yellow;
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

button.plain { background:none; border:none; text-align: left;}

button.plain:hover { cursor: pointer;}

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
