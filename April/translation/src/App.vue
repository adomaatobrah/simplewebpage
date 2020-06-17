<template>
  <div id="app">
    <div class="form-group">
      <label for="userenglish">Enter English text </label>
      <textarea 
        id = "userenglish" 
        name='text'
        v-model="input.english">
      </textarea><br><br>
      <label for="usergerman">Enter German text </label>
      <textarea 
        id = "usergerman" 
        name='text'
        v-model="input.german">
      </textarea><br><br>
      <button @click="submit()">continue</button>
    </div>
    <div class="results">
      <br>
      Your translation:
      <p style="font-size: 30px;">
      <span class="tooltip keep-spaces" v-for="(word, ind) in inputdata.predictions" 
       v-bind:style="{ 'background-color': word[0][1] }">{{word[0][0]}}
        <div id=ind class="tooltiptext">
          <ol>
            <li v-for="(i in word[1]">
              <button>
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
        german: '',
      },
      inputdata: {"translation": '',
                  "predictions": []
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
