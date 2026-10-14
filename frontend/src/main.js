import { createApp } from "vue";
// import './style.css'
import { createPinia } from "pinia";
import axios from "axios";
import router from "./router/index.js";
import App from "./App.vue";

const app = createApp(App);
app.use(createPinia());
app.use(router);

const savedToken = localStorage.getItem("accessToken");
if (savedToken) {
  axios.defaults.headers.common["Authorization"] = `Bearer ${savedToken}`;
}

app.mount("#app");
