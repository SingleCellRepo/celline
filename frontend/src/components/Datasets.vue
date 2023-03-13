<template>
  <div id="left_panel">
    <div id="panel_content">
      <div v-for="gse in gses" :key="gse.runid">
        <v-btn
          variant="flat"
          color="blue-grey"
          :rounded="0"
          v-if="gse.runid == selected?.runid"
        >
          {{ gse.runid }}</v-btn
        >
        <v-btn variant="flat" :rounded="0" v-else @click="select_gse(gse)">
          {{ gse.runid }}</v-btn
        >
      </div>
    </div>
  </div>
  <div id="right_panel">
    <p class="text-h5 font-weight-black">
      {{ selected?.runid }}
    </p>
    <p class="text-subtitle-1 font-weight-bold">
      {{ selected?.title }}
    </p>
    <a :href="selected?.link" target="blank" class="text-decoration-none">{{
      selected?.link
    }}</a>
    <v-spacer></v-spacer>
    <p class="text-caption text-medium-emphasis" id="summary">
      {{ selected?.summary }}
    </p>
    <v-expansion-panels id="panel">
      <v-expansion-panel
        v-for="data in selected?.target_gsms"
        :key="data.accession"
        collapse-icon="mdi"
      >
        <v-expansion-panel-title>
          <v-layout row wrap>
            {{ data.accession }} ({{ data.title }})
          </v-layout></v-expansion-panel-title
        >
        <v-expansion-panel-text>
          <div class="grid sm:grid-cols-4 gap-4 items-stretch">
            <v-btn dark color="red">Delete</v-btn>
            <v-btn dark color="red">Delete</v-btn>
            <v-btn dark color="red">Delete</v-btn>
            <v-btn dark color="red">Delete</v-btn>
          </div>
        </v-expansion-panel-text>
      </v-expansion-panel>
    </v-expansion-panels>

    <v-row justify="center">
      <v-dialog v-model="add_gsm_open" scrollable width="50%">
        <template v-slot:activator="{ props }">
          <v-btn color="primary" v-bind="props" id="add_gsm_button">
            Manage
          </v-btn>
        </template>
        <v-card>
          <v-card-title>Select Target GSM</v-card-title>
          <v-divider></v-divider>
          <div
            v-for="gsm in selected?.gsms"
            :key="gsm.accession"
            :value="gsm.accession"
          >
            <v-checkbox
              v-model="selected_gsms"
              :label="gsm.title + '(' + gsm.accession + ')'"
              :value="gsm.accession"
            >
            </v-checkbox>
          </div>
          <v-divider></v-divider>
          <v-card-actions>
            <v-btn color="blue-darken-1" variant="text" @click="dialog = false">
              Close
            </v-btn>
            <v-btn color="blue-darken-1" variant="text" @click="dialog = false">
              Save
            </v-btn>
          </v-card-actions>
        </v-card>
      </v-dialog>
    </v-row>
  </div>
  <v-dialog v-model="dialog" width="800">
    <template v-slot:activator="{ props }">
      <v-btn
        color="indigo-darken-2"
        v-bind="props"
        id="add_root_button"
        :rounded="0"
      >
        Add New
      </v-btn>
    </template>
    <v-card>
      <v-card-title>
        <span class="text-h5">Search GSE or GSM ID</span>
      </v-card-title>
      <div id="search_field">
        <v-text-field
          v-model="runid"
          label="GSE or GSM ID"
          :rules="rule"
          :loading="searching"
          variant="underlined"
        ></v-text-field>
      </div>
      <v-card-actions>
        <v-spacer></v-spacer>
        <v-btn
          color="green-darken-1"
          variant="text"
          @click="dialog = false"
          :disabled="searching"
        >
          Cancel
        </v-btn>
        <v-btn
          color="green-darken-1"
          variant="text"
          @click="search"
          :disabled="searching"
        >
          Search
        </v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>

<script lang="ts">
import { Options, Vue } from "vue-class-component";
import axios, { AxiosError, AxiosResponse } from "axios";
type GSM = {
  accession: string;
  title: string;
};
type GSE = {
  runid: string;
  title: string;
  link: string;
  summary: string;
  species: string;
  raw_link: string;
  gsms: GSM[];
  target_gsms: GSM[];
};
@Options({
  props: {
    msg: String,
  },
})
export default class LeftPanel extends Vue {
  gses: GSE[] = [];
  selected: GSE | null = null;
  selected_gsms: string[] = [];
  show_rightclick_menu = false;
  public refresh(): void {
    axios({
      url: `http://localhost:8000/gses`,
      method: "GET",
    })
      .then((res: AxiosResponse) => {
        this.gses = res.data;
        if (this.gses.length > 0 && this.selected == null) {
          this.selected = this.gses[0];
        }
        const gsms = this.selected?.target_gsms.map((d) => d.accession);
        if (gsms != undefined) {
          this.selected_gsms = gsms;
        }
      })
      .catch((e: AxiosError<{ error: string }>) => {
        console.log(e.message);
      });
  }
  public created(): void {
    this.refresh();
  }

  public select_gse(gse: GSE) {
    this.selected = gse;
    const gsms = this.selected?.target_gsms.map((d) => d.accession);
    if (gsms != undefined) {
      this.selected_gsms = gsms;
    }
  }

  dialog = false;
  add_gsm_open = false;
  dialogm1 = "";
  runid = "";
  rule = [
    (value: string) => {
      if (value.startsWith("GSE") || value.startsWith("GSM")) return true;

      return "ID should be GSE ID or GSM ID.";
    },
  ];
  searching = false;
  public search() {
    this.searching = true;
    axios({
      url: `http://localhost:8000/addgsm?id=${this.runid}`,
      method: "GET",
    })
      .then((res: AxiosResponse) => {
        this.searching = false;
        this.dialog = false;
        this.refresh();
      })
      .catch((e: AxiosError<{ error: string }>) => {
        console.log(e.message);
        this.searching = false;
      });
  }
  // Right
}
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style lang="scss" scoped>
#left_panel {
  overflow-y: scroll;
  overflow-x: hidden;
  width: 150px;
  height: calc(100vh - 60px - 52px - 48px);
  padding: 0;
  position: fixed;
  left: 0;
  -ms-overflow-style: none;
  border-right: 2px rgb(167, 167, 167) solid;
  #panel_content {
    button {
      width: 100%;
      height: 50px;
    }
  }
}

#left_panel::-webkit-scrollbar {
  display: none;
}
#right_panel {
  width: calc(100vw - 200px);
  height: calc(100vh - 200px);
  margin: 0 20px 0 150px;
  #panel {
    margin: 30px 0 0 0;
  }
  #summary {
    margin: 0.5em 0 0 0;
  }
  #add_gsm_button {
    position: fixed;
    bottom: 2em;
  }
}
#add_root_button {
  position: fixed;
  height: 50px;
  width: 150px;
  bottom: 0px;
  color: white;
  left: 0;
}
#search_field {
  width: 80%;
  margin: 2em 10%;
}
#position_absolute {
  position: absolute;
}
</style>
