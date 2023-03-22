<template>
  <div id="settings">
    <v-row justify="center">
      <v-dialog
        v-model="dialog"
        fullscreen
        :scrim="false"
        transition="dialog-bottom-transition"
      >
        <template v-slot:activator="{ props }">
          <v-btn id="icon" color="blue-grey" icon="mdi-cog" v-bind="props">
          </v-btn>
        </template>
        <v-card>
          <v-toolbar dark color="blue-grey">
            <v-btn icon @click="dialog = false">
              <v-icon>mdi-close</v-icon>
            </v-btn>
            <v-toolbar-title>Settings</v-toolbar-title>
            <v-spacer></v-spacer>
            <v-toolbar-items>
              <v-btn variant="text" @click="dialog = false"> Save </v-btn>
            </v-toolbar-items>
          </v-toolbar>
          <div id="contents">
            <div class="text-h5">Remote Servers</div>
            <v-expansion-panels id="server_list">
              <v-expansion-panel
                v-for="server in servers"
                :key="server.name"
                @click="on_edit_server(server.name)"
              >
                <v-expansion-panel-title>
                  <v-btn
                    @click.stop="delete_server(server.name)"
                    icon="mdi-trash-can-outline"
                    size="x-small"
                    variant="flat"
                    rounded="lg"
                    color="error"
                  ></v-btn>
                  <span id="instructions"
                    >{{ server.name }} ({{ server.ip }})</span
                  >
                </v-expansion-panel-title>
                <v-expansion-panel-text v-if="current_server != null">
                  <v-text-field
                    label="IP address"
                    :placeholder="current_server.ip"
                    v-model="current_server.ip"
                    type="string"
                  ></v-text-field>
                  <v-text-field
                    label="Secret key (Full path)"
                    :placeholder="current_server.secretkey_path"
                    v-model="current_server.secretkey_path"
                    type="string"
                    :rules="secretkey_rule"
                  ></v-text-field>
                  <v-text-field
                    label="User name"
                    :placeholder="current_server.uname"
                    v-model="current_server.uname"
                    type="string"
                  ></v-text-field>
                  <v-text-field
                    label="Port"
                    :placeholder="current_server.port.toString()"
                    v-model="current_server.port"
                    type="number"
                  ></v-text-field>
                  <v-btn color="success" @click="apply">Apply</v-btn>
                </v-expansion-panel-text>
              </v-expansion-panel>
            </v-expansion-panels>
            <v-col>
              <v-btn icon="mdi-plus" color="info" id="add_new_server"></v-btn>
            </v-col>
          </div>
        </v-card>
      </v-dialog>
    </v-row>
  </div>
</template>

<script lang="ts">
import axios from "axios";
import { Options, Vue } from "vue-class-component";
type Server = {
  name: string;
  ip: string;
  uname: string;
  secretkey_path: string;
  port: number;
};

export default class Settings extends Vue {
  dialog = false;
  public server_lists: Server[] = [];
  public current_server: Server | null = null;
  public secretkey_rule = [
    (value: string) => {
      if (this.server_lists.map((d) => d.name).includes(value))
        return `${value} is already used as server name`;
      else return true;
    },
  ];
  created() {
    this.update_server_data();
  }
  private update_server_data() {
    this.server_lists = [];
    axios.get(`http://localhost:8000/servers`).then((response) => {
      if (typeof response.data === "string") {
        console.error(`Server fetch error: ${response.data}`);
      } else {
        this.server_lists = response.data;
      }
    });
  }
  public get servers() {
    return this.server_lists;
  }
  public on_edit_server(server_name: string) {
    if (server_name != this.current_server?.name) {
      const result = this.server_lists.find((d) => d.name == server_name);
      if (result == undefined) {
        this.current_server = null;
      } else {
        this.current_server = result;
      }
    }
  }
  public apply() {
    if (this.current_server != null) {
      console.log(this.current_server.ip);
      axios
        .post(
          `http://localhost:8000/servers?id=${this.current_server.name}`,
          this.current_server
        )
        .then((response) => {
          if (response.data != "SUCESS") {
            console.error(`Server fetch error: ${response.data}`);
          } else {
            console.log("update OK");
          }
        });
    }
  }
  public delete_server(target_server_name: string) {
    axios
      .delete(`http://localhost:8000/servers?id=${target_server_name}`)
      .then((response) => {
        if (response.data != "SUCESS") {
          console.error(`Error: ${response.data}`);
        }
      });
    this.update_server_data();
  }
}
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style lang="scss" scoped>
#contents {
  margin: 1em;
  span#instructions {
    margin: 0 0 0 1em;
  }
  #server_list {
    margin: 1em 0 0 0;
  }
  #add_new_server {
    position: fixed;
    right: 1em;
    bottom: 1em;
  }
}
</style>
