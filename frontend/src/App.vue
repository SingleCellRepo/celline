<template>
  <v-app :theme="theme.value">
    <Header class="fix_position"></Header>
    <v-tabs
      v-model="tab"
      color="deep-purple-accent-4"
      align-tabs="center"
      fixed-tabs
      class="fix_position"
      id="tab"
    >
      <v-tab :value="1">Datasets</v-tab>
      <v-tab :value="2">Runs</v-tab>
      <v-tab :value="3">Results</v-tab>
    </v-tabs>
    <v-main id="content">
      <v-window v-model="tab">
        <v-window-item v-for="n in 3" :key="n" :value="n">
          <v-container fluid>
            <Datasets v-if="n == 1"> </Datasets>
          </v-container>
        </v-window-item>
      </v-window>
    </v-main>
  </v-app>
</template>

<script lang="ts">
import { Options, Vue } from "vue-class-component";
import Header from "./components/Header.vue";
import { ref } from "vue";
import axios, { AxiosError, AxiosResponse } from "axios";
import Datasets from "./components/Datasets.vue";

const URL = "http://localhost:8000/";
@Options({
  components: {
    Header,
    Datasets,
  },
})
export default class App extends Vue {
  theme = ref("light");
  tab = 1;
}
</script>

<style lang="scss" scoped>
#app {
  font-family: Avenir, Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  text-align: center;
  color: #2c3e50;
  margin-top: 60px;
  .fix_position {
    position: fixed;
  }
  #content {
    margin: 110px 0 0 0;
  }
  #tab {
    margin: 60px 0 0 0;
    z-index: 15;
    width: 100vw;
    background-color: white;
  }
}
</style>
