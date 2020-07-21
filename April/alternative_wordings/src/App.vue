<template>
  <div id="app">
    <div class="form-group">
    <h2>Exploring alternative wordings</h2>
      <textarea 
        id = "userenglish" 
        name='text'
        v-model="inputText"
        rows="4" cols="50"
        required>
      </textarea><br><br>
      <button @click="getResult(inputText)">continue</button>
  </div>

   <div class="results"><br>
    <ul>
    <li v-for="alt in inputData.colorCoding" class="tooltip">
      <button @click="getResult(inputText)" style="font-size: 15px;" class = "plain">
        <span v-for="chunk in alt" 
              v-bind:style="{ 'background-color': colors[chunk[1]] }">
              {{ chunk[0] }}
          </span>
      </button>
      <br>
    </li>
    </ul>
    </div>
 </div>
  </div>
</template>

<script>
export default {
  data() {
    return {
      inputText: '',
      inputData: {"alternatives" : [],
                  "scores" : [],
                  "colorCoding" : []
                          },
      colors: [ 'white', '#ABE3BB', '#E4B0AF', '#3DA1B8', '#E4E2AF', '#B8473D', '#B39FCF', '#30915F']
    };
  },

  methods: {
    async getResult(inputText){
        var url = new URL("/api/result", window.location);

        var params = {
          english:inputText,
        };
        url.searchParams.append('q', JSON.stringify(params));

        const res = await fetch(url);
        const input = await res.json();
        this.inputData = input;      
   },
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
ul {
  line-height:300%
}

.results {
  text-align: left;
  margin-left: 10%;
  margin-right: 10%
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

button.plain { background:none; border:none; text-align: left; }

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
