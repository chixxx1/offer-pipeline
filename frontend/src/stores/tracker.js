import { defineStore } from "pinia";
import axios from "axios";

export const useTrackerStore = defineStore("tracker", {
  state: () => ({
    vacancies: [],
    isLoading: false,
    error: null,
  }),

  actions: {
    async fetchVacancies() {
      this.isLoading = true;
      this.error = null;

      try {
        const response = await axios.get("api/vacancies/");
        this.vacancies = response.data;
      } catch (err) {
        this.error = "Не удалось получить вакансии";
        console.log(err);
      } finally {
        this.isLoading = false;
      }
    },
  },
});
