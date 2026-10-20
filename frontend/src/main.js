import { createApp } from "vue";
// import './style.css'
import { createPinia } from "pinia";
import axios from "axios";
import router from "./router/index.js";
import App from "./App.vue";
import { useAuthStore } from "./stores/auth";

const app = createApp(App);
app.use(createPinia());
app.use(router);

const savedToken = localStorage.getItem("accessToken");
if (savedToken) {
  axios.defaults.headers.common["Authorization"] = `Bearer ${savedToken}`;
}

axios.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;

    if (error.response && error.response.status === 401 && !originalRequest._retry) {
      const refreshToken = localStorage.getItem("refreshToken");

      if (refreshToken) {
        originalRequest._retry = true;
        try {
          const response = await axios.post("/api/auth/refresh/", {
            refresh: refreshToken,
          });
          const { access } = response.data;

          localStorage.setItem("accessToken", access);
          axios.defaults.headers.common["Authorization"] = `Bearer ${access}`;
          originalRequest.headers["Authorization"] = `Bearer ${access}`;
          return axios(originalRequest);
        } catch (refreshError) {
          const authStore = useAuthStore();
          authStore.logout();
          router.push("/login");
          return Promise.reject(refreshError);
        }
      } else {
        const authStore = useAuthStore();
        authStore.logout();
        router.push("/login");
        return Promise.reject(error);
      }
    }

    return Promise.reject(error);
  }
);

app.mount("#app");
