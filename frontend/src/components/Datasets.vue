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
          <v-progress-circular
            indeterminate
            color="amber"
            size="25"
            class="loading_icon"
          ></v-progress-circular>
          {{ gse.runid }}</v-btn
        >
        <v-btn variant="flat" :rounded="0" v-else @click="select_gse(gse)">
          <v-progress-circular
            indeterminate
            color="amber"
            size="25"
            class="loading_icon"
          ></v-progress-circular>
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
    <br />
    <v-chip
      variant="elevated"
      v-for="sp in selected?.species"
      v-bind:key="sp"
      id="spieces_chip"
    >
      <v-icon start icon="mdi-dna"></v-icon>
      {{ sp }}
    </v-chip>
    <v-btn
      color="error"
      prepend-icon="mdi-delete"
      @click="delete_gse"
      class="header_instruction_button"
    >
      Delete
    </v-btn>
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
            <v-btn icon dark @click="dialog = false">
              <v-icon>mdi-close</v-icon>
            </v-btn>
            <v-toolbar-title
              >Data download of {{ selected?.runid }}</v-toolbar-title
            >
            <v-spacer></v-spacer>
            <v-toolbar-items>
              <v-btn variant="text" @click="dialog = false"> Save </v-btn>
            </v-toolbar-items>
          </v-toolbar>
          <v-list lines="one" subheader>
            <v-list-subheader>Download Settings</v-list-subheader>
            <v-list-item
              title="Download System"
              subtitle="Select the system you wish to use for downloading this data."
            >
              <v-list-item>
                <v-select
                  v-model="dump_strategy"
                  :items="dump_strategies"
                  label="Download strategy"
                  required
                ></v-select>
                <v-row>
                  <v-select
                    v-model="dump_strategy_server.jobsystem"
                    :items="['PBS']"
                    label="Job System"
                    required
                    :disabled="dump_strategy != 'Job system'"
                  ></v-select>
                  <v-text-field
                    v-model="dump_strategy_server.cluster_name"
                    label="Cluster server name"
                    required
                    :disabled="dump_strategy != 'Job system'"
                  ></v-text-field>
                </v-row>
                <v-text-field
                  v-model="dump_strategy_nthread"
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

    <v-expansion-panels id="panel">
      <v-expansion-panel
        v-for="data in selected?.target_gsms"
        :key="data.accession"
        collapse-icon="mdi"
        v-model="target_sample"
        @click="edit_sample(data.accession)"
      >
        <v-expansion-panel-title>
          <v-layout row wrap>
            {{ data.accession }} ({{ data.title }})
          </v-layout></v-expansion-panel-title
        >
        <v-expansion-panel-text>
          <div class="grid sm:grid-cols-4 gap-4 items-stretch">
            <v-text-field
              v-model="target_sample_name"
              :counter="10"
              label="Customize sample name"
              required
              @change="on_samplename_edit"
            ></v-text-field>
            <v-card :loading="srrs_in_selected_gsm.length <= 0">
              <v-card-text>
                <v-table density="compact">
                  <thead>
                    <tr>
                      <th class="text-left">File type</th>
                      <th class="text-left">Runs</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr v-for="item in srrs_in_selected_gsm" :key="item.run_id">
                      <td>
                        <v-chip
                          class="ma-2"
                          label
                          prepend-icon="mdi-checkbox-marked-circle"
                          color="green"
                          >{{ item.filetype }}</v-chip
                        >
                      </td>
                      <td>
                        <v-chip-group>
                          <v-chip
                            v-for="runs in item.sc_runs"
                            v-bind:key="runs.cloud_path"
                            label
                          >
                            {{ runs.cloud_path }}
                          </v-chip>
                        </v-chip-group>
                      </td>
                    </tr>
                  </tbody>
                </v-table>
              </v-card-text>
            </v-card>
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
          <v-card-title id="manage_action_title"
            >Select Target GSM</v-card-title
          >
          <v-divider></v-divider>
          <div id="manage_action_content">
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
          </div>
          <v-divider></v-divider>
          <v-card-actions id="manage_action_btn">
            <v-btn color="blue-darken-1" variant="text" @click="dialog = false">
              Close
            </v-btn>
            <v-btn color="blue-darken-1" variant="text" @click="postgsm">
              Save
            </v-btn>
          </v-card-actions>
        </v-card>
      </v-dialog>
    </v-row>
  </div>
  <v-dialog v-model="dialog" width="800" persistent>
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
        <span class="text-h5">Search GSE ID</span>
      </v-card-title>
      <div id="search_field">
        <v-text-field
          v-model="runid"
          label="GSE ID"
          :rules="rule"
          :loading="searching"
          variant="underlined"
        ></v-text-field>
        <v-btn flat id="search_button" @click="search" :disabled="search_error"
          ><v-icon icon="mdi-magnify"></v-icon>Search</v-btn
        >
      </div>
      <div id="search_results">
        <v-alert
          type="success"
          :title="'Add ' + search_result.runid + '?'"
          :text="search_result.title"
          v-if="search_result != null"
        ></v-alert>
        <v-alert
          type="error"
          title="GSE Search Error"
          :text="search_result_error_content"
          v-if="search_result_error_content != ''"
        ></v-alert>
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
          :disabled="searching || search_result == null"
          @click="addgse"
        >
          Add This Project
        </v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>

<script lang="ts">
import { Options, Vue } from "vue-class-component";
import axios, { AxiosError, AxiosResponse } from "axios";
import { stringLiteral } from "@babel/types";
import Download from "./Download.vue";
import { defineComponent, ref } from "vue";
type GSM = {
  accession: string;
  title: string;
};
type GSE = {
  runid: string;
  title: string;
  link: string;
  summary: string;
  species: string[];
  raw_link: string;
  gsms: GSM[];
  target_gsms: GSM[];
};
type SRR = {
  filetype: string;
  run_id: string;
  sc_runs: {
    cloud_path: string;
    filesize: number;
    lane: string;
    readtype: string;
  }[];
};
@Options({
  components: {
    Download,
  },
})
export default class LeftPanel extends Vue {
  gses: GSE[] = [];
  selected: GSE | null = null;
  selected_gsms: string[] = [];
  donwload_dialog = false;
  public refresh(): void {
    axios({
      url: `http://localhost:8000/gses`,
      method: "GET",
    })
      .then((res: AxiosResponse) => {
        this.gses = res.data;

        if (this.gses.length > 0) {
          if (this.selected == null) this.selected = this.gses[0];
          else {
            const update_target = this.gses.find(
              (d) => d.runid == this.selected?.runid
            );
            if (update_target != undefined) {
              this.selected = update_target;

              this.gse_species = this.selected.species;
            }
          }
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
  gse_species: string[] = [];
  dialog = false;
  add_gsm_open = false;
  search_result: GSE | null = null;
  search_result_error_content = "";
  search_error = true;
  runid = "";
  rule = [
    (value: string) => {
      if (value.startsWith("GSE")) {
        if (this.gses.map((d) => d.runid).includes(value)) {
          return "ID is already contained.";
        }
        this.search_error = false;
        return true;
      }
      return "ID should be GSE ID or GSM ID.";
    },
  ];
  searching = false;
  public search() {
    this.searching = true;
    axios({
      url: `http://localhost:8000/getgse?id=${this.runid}`,
      method: "GET",
    })
      .then((res: AxiosResponse) => {
        this.searching = false;
        if (typeof res.data === "string") {
          this.search_result_error_content = res.data;
          this.search_result = null;
        } else {
          this.search_result = res.data;
          this.search_result_error_content = "";
        }
        this.search_error = true;
      })
      .catch((e: AxiosError<{ error: string }>) => {
        console.log(e.message);
        this.searching = false;
      });
  }
  public addgse() {
    this.searching = true;
    axios({
      url: `http://localhost:8000/addgse?id=${this.runid}`,
      method: "GET",
    })
      .then((res: AxiosResponse) => {
        this.searching = false;
        this.dialog = false;
        this.search_result_error_content = "";
        this.search_result = null;
        this.search_error = true;
        this.refresh();
      })
      .catch((e: AxiosError<{ error: string }>) => {
        console.log(e.message);
        this.searching = false;
      });
  }
  // Right
  public postgsm() {
    axios
      .post(`http://localhost:8000/postgsm?id=${this.selected?.runid}`, {
        gsm_id: this.selected_gsms,
        sample_name: this.gses
          .find((data) => data.runid == this.selected?.runid)
          ?.gsms.filter((d) => this.selected_gsms.includes(d.accession))
          ?.map((d) => d.title),
      })
      .then((response) => {
        this.refresh();
      });
    this.add_gsm_open = false;
  }
  target_sample = "";
  target_sample_name = "";
  public edit_sample(accession: string) {
    if (accession != undefined) {
      if (this.target_sample == accession) return;
      this.target_sample = accession;
      this.getsrr(accession);
    }
  }
  public on_samplename_edit() {
    if (this.target_sample_name != "") {
      const target_gsm_index = this.selected?.target_gsms?.findIndex(
        (d) => d.accession == this.target_sample
      );
      if (target_gsm_index != undefined) {
        this.gses[
          this.gses.findIndex((d) => d.runid == this.selected?.runid)
        ].gsms[target_gsm_index].title = this.target_sample_name;
        this.gses[
          this.gses.findIndex((d) => d.runid == this.selected?.runid)
        ].target_gsms[target_gsm_index].title = this.target_sample_name;
        axios
          .post(`http://localhost:8000/postgsm?id=${this.selected?.runid}`, {
            gsm_id: this.selected?.target_gsms.map((d) => d.accession),
            sample_name: this.gses
              .find((data) => data.runid == this.selected?.runid)
              ?.target_gsms?.map((d) => d.title),
          })
          .then((response) => {
            this.refresh();
          });
      }
      // this.refresh();
    }
  }
  public delete_gse() {
    alert("DELETE Action");
  }
  srrs_in_selected_gsm: SRR[] = [];
  getsrr(gsm_id: string) {
    this.srrs_in_selected_gsm = [];
    axios.get(`http://localhost:8000/srr?id=${gsm_id}`).then((response) => {
      this.srrs_in_selected_gsm = response.data;
    });
  }
  dump_strategies: string[] = [
    "Job system",
    "Nohup",
    "Direct download (NOT Recommended)",
  ];
  dump_strategy = this.dump_strategies[0];
  dump_strategy_server: {
    jobsystem: string;
    cluster_name: string;
  } = {
    jobsystem: "PBS",
    cluster_name: "",
  };
  dump_strategy_nthread = 1;
  dump_strategy_nthread_rule = [
    (value: number) => {
      if (value > 0) return true;
      return "Please set integer number";
    },
  ];
  dump_target_filetypes = ["raw type (e.g fastq, bam)", "processed data"];
  dump_target_filetype = this.dump_target_filetypes[0];
  public dump() {
    axios
      .get(`http://localhost:8000/dump?id=${this.selected?.runid}`)
      .then((response) => {
        console.log("OK");
      });
  }
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
  padding: 0 0 1em 0;
  overflow-y: scroll;
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
  #spieces_chip {
    margin: 0 0.2em 0 0;
  }
  .header_instruction_button {
    margin: 0 0 0 0.5em;
    border-radius: 100px;
    height: 35px;
  }
  .header_instruction_button_inline {
    display: inline;
  }
}
#manage_action_btn {
  position: fixed;
  bottom: 0;
  background-color: white;
  width: 100%;
}
#manage_action_content {
  padding: 50px 0;
}
#manage_action_title {
  position: fixed;
  z-index: 10;
  background-color: white;
  width: 100%;
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
  margin: 1em 1em 1em 2em;
  display: flex;
  justify-content: flex-start;
}
#search_button {
  height: 50px;
}
#search_results {
  margin: 0 3em 1em 3em;
}
#position_absolute {
  position: absolute;
}
.loading_icon {
  margin: 0 0.5em 0 0;
}
#dump_start_btn {
  display: flex;
  justify-content: center;
}
</style>
