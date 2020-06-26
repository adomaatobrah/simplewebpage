<template>
  <div id="app">
    <div class="form-group">
      <label for="userenglish">English text </label><br>
      <textarea 
        id = "userenglish" 
        name='text'
        v-model="input.english"
        rows="4" cols="50">
      </textarea><br><br>
      <br> 
      <label for="firstword">Beginning of translation</label><br>
      <textarea 
        id = "firstword" 
        name='text'
        v-model="input.firstword"
        rows="4" cols="50">
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
        {{ wholeTranslation.translation }}
    </p>
      English:
      <p style="font-size: 30px;">
        {{ wholeTranslation.newEnglish }}
      </p>
      
      <br>
     

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
      inputdata: {"translation": '',
                  "predictions": [],
                  "colors": [],
                  "decoded_tokens": []
                },
      msg: '',
      wholeTranslation: {"translation": '',
                         "expected": '',
                         "newEnglish": ''},
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
