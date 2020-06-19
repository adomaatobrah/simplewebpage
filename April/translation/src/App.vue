<template>
  <div id="app">
    <div class="form-group">
      <label for="userenglish">Enter English text </label>
      <textarea 
        id = "userenglish" 
        name='text'
        v-model="input.english"
        rows="4" cols="50">
      </textarea><br><br>
      <label for="usergerman">Enter German text </label>
      <textarea 
        id = "usergerman" 
        name='text'
        v-model="input.german"
        rows="4" cols="50">
      </textarea><br><br>
      <button @click="submit()">continue</button>
    </div>
    <div class="results">
      <br>
      Your translation:
      <p style="font-size: 30px;">
      <span class="tooltip" v-for="(word, ind) in inputdata.decoded_words" 
       v-bind:style="{ 'background-color': inputdata.colors[ind] }">{{word}}
        <div id=ind class="tooltiptext">
          <ol>
            <li v-for="(i in inputdata.predictions[ind]">
              <button @click="recalculate(i, ind)">
                '{{i}}'
              </button>
            </li>
          </ol>
        </div>
      </span>
    </p>
      Expected translation:
      <p style="font-size: 30px;">
        {{ inputdata.translation }}
        <br><br>
        {{ msg }}
      </p>
      <br>
      <span style="background-color:lime;">Expected</span> (top prediction)<br>
       <span style="background-color:yellow;">Somewhat predictable</span> (appeared in the first 10 predictions)<br>
       <span style="background-color:red;">Somewhat unpredictable</span> (didn't appear in the first 10 predictions)<br>
   </div>
  </div>
</template>

<script>

export default {
  data() {
    return {
      input: {
        english: '',
        german: '',
      },
      inputdata: {"translation": '',
                  "predictions": [],
                  "colors": [],
                  "decoded_words": []
                },
      msg: ''
    };
  },


  methods: {
   async submit(){
    var url = new URL("http://localhost:5000/result"),
     params = {english:this.input.english, german:this.input.german}
     Object.keys(params).forEach(key => url.searchParams.append(key, params[key]))
     const res = await fetch(url);
     const input = await res.json();
     this.inputdata = input;
    },
    async recalculate(changedword, index){
     this.$set(this.inputdata.decoded_words, index, changedword);
     var newinputstr = this.inputdata.decoded_words.join('').replace(/\u00a0/g, ' ');
     this.msg=newinputstr;

     var url = new URL("http://localhost:5000/result"),
     params = {english:this.input.english, german:newinputstr}
     Object.keys(params).forEach(key => url.searchParams.append(key, params[key]))
     const res = await fetch(url);
     const input = await res.json();
     this.inputdata = input;
     this.input = {
       english: this.input.english,
       german: newinputstr,
     };

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
