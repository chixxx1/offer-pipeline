import { defineStore } from "pinia";
import axios from "axios";

export const useSearchStore = defineStore("search", {
  state: () => ({
    query: "",
    results: [],
    isLoading: false,
    error: null,
    filters: {
      experience: [],
      work_format: [],
      salary_from: null,
      work_schedule_by_days: [],
      employment_form: [],
    },
  }),

  actions: {
    async search() {
      if (!this.query.trim()) return;

      this.isLoading = true;
      this.error = null;

      try {
        const response = await axios.post("/api/vacancies/search/", {
          query: this.query,
          ...this.filters,
        });
        this.results = response.data;
      } catch (err) {
        this.error = "Не удалось выполнить поиск";
        console.error(err);
      } finally {
        this.isLoading = false;
      }
    },
  },
});
