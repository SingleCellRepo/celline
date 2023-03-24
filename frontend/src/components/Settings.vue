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
          <v-btn
            id="icon"
            color="blue-grey"
            icon="mdi-cog"
            v-bind="props"
            @click="connetion_check"
          >
          </v-btn>
        </template>
        <v-card>
          <v-toolbar dark color="blue-grey">
            <v-btn icon @click="dialog = false">
              <v-icon>mdi-close</v-icon>
            </v-btn>
            <v-toolbar-title>Settings</v-toolbar-title>
            <v-spacer></v-spacer>
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
                  <v-icon
                    icon="mdi-check-circle"
                    color="green-darken-2"
                    v-if="connections[server.name] == 'sucess'"
                  ></v-icon>
                  <v-progress-circular
                    indeterminate
                    color="blue-darken-2"
                    :width="3"
                    v-if="connections[server.name] == 'connecting'"
                  ></v-progress-circular>
                  <v-icon
                    icon="mdi-alert-circle"
                    color="error"
                    v-if="connections[server.name] == 'failed'"
                  ></v-icon>
                  <span id="instructions"
                    >{{ server.name }} ({{ server.ip }})</span
                  >
                </v-expansion-panel-title>
                <v-expansion-panel-text v-if="current_server != null">
                  <v-btn
                    @click.stop="delete_server(server.name)"
                    icon="mdi-trash-can-outline"
                    size="x-small"
                    variant="flat"
                    rounded="lg"
                    color="error"
                  ></v-btn
                  >&nbsp;Delete
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
              <v-row justify="center">
                <v-dialog v-model="add_new_trigger" width="800">
                  <template v-slot:activator="{ props }">
                    <v-btn
                      icon="mdi-plus"
                      color="info"
                      id="add_new_server"
                      v-bind="props"
                    ></v-btn>
                  </template>
                  <v-card>
                    <v-card-title>Add new server</v-card-title>
                    <v-card-item
                      ><v-text-field
                        label="Server name"
                        v-model="new_server_name"
                        :rules="new_server_name_rule"
                      ></v-text-field>
                      <v-text-field
                        label="IP address"
                        v-model="new_server_ip"
                      ></v-text-field>
                      <v-text-field
                        label="Username"
                        v-model="new_server_uname"
                      ></v-text-field>
                      <v-text-field
                        label="Port"
                        v-model="new_server_port"
                      ></v-text-field>
                      <v-text-field
                        label="Secret Key Path"
                        v-model="new_server_secretkey_path"
                      ></v-text-field>
                    </v-card-item>
                    <v-card-actions>
                      <v-spacer></v-spacer>
                      <v-btn
                        color="green-darken-1"
                        variant="text"
                        @click="add_new_trigger = false"
                      >
                        Cancel
                      </v-btn>
                      <v-btn
                        color="green-darken-1"
                        variant="text"
                        @click="add_new_server"
                      >
                        Add
                      </v-btn>
                    </v-card-actions>
                  </v-card>
                </v-dialog>
              </v-row>
            </v-col>
          </div>
        </v-card>
      </v-dialog>
    </v-row>
  </div>
</template>

<script lang="ts">
import { Server } from "src/types";
import axios from "axios";
import { Options, Vue } from "vue-class-component";
type ServerStatus = {
  name: string;
  server: Server;
  connection_testing: boolean;
  sucess_connection: boolean;
};
export default class Settings extends Vue {
  dialog = false;
  add_new_trigger = false;
  new_server_name = "";
  new_server_ip = "";
  new_server_uname = "";
  new_server_secretkey_path = "";
  new_server_port = 22;
  new_server_name_rule = [
    (value: string) => {
      if (this.is_exist(value)) {
        return true;
      }
      return `${value} is already used as server name`;
    },
  ];
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
    this.update_server_data((status) => {
      if (status) {
        this.connetion_check();
      }
    });
  }
  private update_server_data(
    callback: (status: boolean) => void = () => console.log("")
  ) {
    this.server_lists = [];
    axios.get(`http://localhost:8000/servers`).then((response) => {
      if (typeof response.data === "string") {
        console.error(`Server fetch error: ${response.data}`);
        callback(false);
      } else {
        this.server_lists = response.data;
        callback(true);
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
  public is_exist(name: string) {
    return this.server_lists.find((d) => d.name == name) == undefined;
  }
  public add_new_server() {
    const server: Server = {
      name: this.new_server_name,
      ip: this.new_server_ip,
      uname: this.new_server_uname,
      secretkey_path: this.new_server_secretkey_path,
      port: this.new_server_port,
    };
    axios
      .post(`http://localhost:8000/servers?id=${this.new_server_name}`, server)
      .then((response) => {
        console.log(response);
        this.update_server_data();
        this.add_new_trigger = false;
      });
  }
  connections: { [name: string]: string } = {};
  connection_error = "";
  public connetion_check() {
    this.connections = {};
    this.servers.forEach((server) => {
      this.connections[server.name] = "connecting";
      axios
        .get(`http://localhost:8000/server_status?id=${server.name}`)
        .then((response) => {
          if (response.data) {
            console.log(`OK: ${server.name}`);
            this.connections[server.name] = "sucess";
          } else {
            this.connections[server.name] = "failed";
            this.connection_error = response.data;
          }
        })
        .catch((reason) => {
          this.connections[server.name] = "failed";
          this.connection_error = reason;
        });
    });
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
