import { defineStore } from "pinia";
import axios from "axios";

export const useAuthStore = defineStore("auth", {
  state: () => ({
    accessToken: localStorage.getItem("accessToken") || null,
    refreshToken: localStorage.getItem("refreshToken") || null,
    user: null,
  }),

  getters: {
    isAuthenticated: (state) => !!state.accessToken,
  },

  actions: {
    async login(username, password) {
      const response = await axios.post("/api/auth/login/", {
        username,
        password,
      });
      this.setTokens(response.data.access, response.data.refresh);
      await this.fetchMe();
    },

    async register(username, email, password) {
      await axios.post("/api/auth/register/", { username, email, password });
      await this.login(username, password);
    },

    setTokens(access, refresh) {
      this.accessToken = access;
      this.refreshToken = refresh;
      localStorage.setItem("accessToken", access);
      localStorage.setItem("refreshToken", refresh);
      axios.defaults.headers.common["Authorization"] = `Bearer ${access}`;
    },

    async fetchMe() {
      const response = await axios.get("/api/auth/me/");
      this.user = response.data;
    },

    async refreshTokens() {
      const response = await axios.post("/api/auth/refresh/", {
        refresh: this.refreshToken,
      });
      const { access, refresh } = response.data;
      this.setTokens(access, refresh);
      return access;
    },

    logout() {
      this.accessToken = null;
      this.refreshToken = null;
      this.user = null;
      localStorage.removeItem("accessToken");
      localStorage.removeItem("refreshToken");
      delete axios.defaults.headers.common["Authorization"];
    },
  },
});
