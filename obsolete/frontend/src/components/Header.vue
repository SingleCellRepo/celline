<template>
  <header>
    <v-toolbar
      dark
      prominent
      image="https://images.unsplash.com/photo-1643780668909-580822430155?ixlib=rb-4.0.3&ixid=MnwxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8&auto=format&fit=crop&w=2664&q=80"
    >
      <!-- <v-toolbar-title id="header_text">Vuetify</v-toolbar-title> -->
      <img alt="Celline" src="../assets/logo_dark.png" id="logo" />
      <v-spacer></v-spacer>

      <v-btn icon>
        <v-icon>mdi-export</v-icon>
      </v-btn>
    </v-toolbar>
  </header>
</template>

<script lang="ts">
import { Options, Vue } from "vue-class-component";

@Options({
  props: {
    msg: String,
  },
})
export default class HelloWorld extends Vue {
  msg!: string;
}
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style lang="scss" scoped>
img#logo {
  margin: 0 0 0 10px;
  height: 40px;
}
header {
  width: 100vw;
  z-index: 20;
  #header_text {
    color: white;
  }
}
</style>
