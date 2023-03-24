<template>
  <div id="download" class="header_instruction_button_inline">
    <v-dialog
      v-model="donwload_dialog"
      fullscreen
      :scrim="false"
      transition="dialog-bottom-transition"
    >
      <template v-slot:activator="{ props }">
        <v-btn
          color="blue-grey"
          prepend-icon="mdi-download"
          class="header_instruction_button"
          dark
          v-bind="props"
        >
          Download
        </v-btn>
      </template>
      <v-card>
        <v-toolbar dark color="blue-grey">
          <v-btn icon dark @click="donwload_dialog = false">
            <v-icon>mdi-close</v-icon>
          </v-btn>
          <v-toolbar-title
            >Data download of {{ selected?.runid }}</v-toolbar-title
          >
          <v-spacer></v-spacer>
        </v-toolbar>
        <v-list lines="one" subheader>
          <v-list-subheader>Download Settings</v-list-subheader>
          <v-list-item
            title="Download System"
            subtitle="Select the system you wish to use for downloading this data."
          >
            <v-list-item>
              <v-select
                v-model="jobinfo.strategy"
                :items="jobinfo.dump_strategies"
                label="Download strategy"
                required
              ></v-select>
              <v-row>
                <v-select
                  v-model="jobinfo.jobsystem"
                  :items="['PBS']"
                  label="Job System"
                  required
                  :disabled="jobinfo.strategy != 'Job system'"
                ></v-select>
                <v-select
                  v-model="jobinfo.calc_server"
                  :items="server_lists.map((d) => d.name)"
                  label="Cluster server name"
                  required
                  :disabled="jobinfo.strategy != 'Job system'"
                ></v-select>
              </v-row>
              <v-text-field
                v-model="jobinfo.nthread"
                label="nthread"
                :rules="dump_strategy_nthread_rule"
              ></v-text-field>
            </v-list-item>
          </v-list-item>
          <v-list-item
            title="Download Target File Type"
            subtitle="Target file type"
          >
            <v-select
              v-model="dump_target_filetype"
              :items="dump_target_filetypes"
              label="Target file type strategy"
              required
            ></v-select>
          </v-list-item>
        </v-list>
        <v-divider></v-divider>

        <div id="dump_start_btn">
          <v-btn
            color="blue-grey"
            prepend-icon="mdi-cloud-upload"
            @click="dump"
          >
            Start Download
          </v-btn>
        </div>
      </v-card>
    </v-dialog>
  </div>
</template>
<script lang="ts">
import axios from "axios";
import { Options, Vue } from "vue-class-component";
import GSE from "./Datasets.vue";
import { Server } from "@/types";
@Options({
  props: {
    selected: GSE,
  },
})
export default class Download extends Vue {
  donwload_dialog = false;
  selected!: GSE | null;
  jobinfo = {
    dump_strategies: [
      "Job system",
      "Nohup",
      "Direct download (NOT Recommended)",
    ],
    server: "",
    strategy: "Job system",
    jobsystem: "PBS",
    calc_server: "",
    nthread: 1,
  };
  dump_strategy_nthread_rule = [
    (value: number) => {
      if (value > 0) return true;
      return "Please set integer number";
    },
  ];
  dump_target_filetypes = ["raw type (e.g fastq, bam)", "processed data"];
  dump_target_filetype = this.dump_target_filetypes[0];

  server_lists: Server[] = [];
  public dump() {
    console.log("DUMP");
  }
  public created(): void {
    this.server_lists = [];
    axios.get(`http://localhost:8000/servers`).then((response) => {
      if (typeof response.data === "string") {
        console.error(`Server fetch error: ${response.data}`);
      } else {
        this.server_lists = response.data;
        console.log(this.server_lists);
      }
    });
  }
}
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style lang="scss" scoped>
.dialog-bottom-transition-enter-active,
.dialog-bottom-transition-leave-active {
  transition: transform 0.2s ease-in-out;
}
.header_instruction_button {
  margin: 0 0 0 0.5em;
  border-radius: 100px;
  height: 35px;
}
</style>
