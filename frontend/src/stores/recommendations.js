import { defineStore } from "pinia";
import axios from "axios";

export const useRecommendationsStore = defineStore("recommendations", {
  state: () => ({
    recommendations: [],
    isLoading: false,
    error: null,
    mode: "recommendations", // 'recommendations' | 'search'
    selectedVariantId: null,
    onlyNew: false,
  }),

  getters: {
    filteredRecommendations(state) {
      let list = state.recommendations.filter((r) => !r.is_dismissed);
      if (state.selectedVariantId) {
        list = list.filter((r) => r.variant === state.selectedVariantId || r.variant === null);
      }
      if (state.onlyNew) {
        list = list.filter((r) => r.is_new);
      }
      return list;
    },
  },

  actions: {
    async loadRecommendations() {
      this.isLoading = true;
      this.error = null;
      try {
        const params = {};
        if (this.selectedVariantId) {
          params.variant_id = this.selectedVariantId;
        }
        if (this.onlyNew) {
          params.only_new = "true";
        }
        const response = await axios.get("/api/recommendations/", { params });
        this.recommendations = response.data || [];
      } catch (err) {
        this.error = "Не удалось загрузить рекомендации";
        console.error(err);
      } finally {
        this.isLoading = false;
      }
    },

    async syncRecommendations() {
      this.isLoading = true;
      this.error = null;
      try {
        const response = await axios.post("/api/recommendations/sync/", {
          variant_id: this.selectedVariantId || null,
        });
        this.recommendations = response.data || [];
        return response.data;
      } catch (err) {
        this.error = "Не удалось обновить рекомендации";
        console.error(err);
        throw err;
      } finally {
        this.isLoading = false;
      }
    },

    async dismissRecommendation(id) {
      try {
        await axios.post(`/api/recommendations/${id}/dismiss/`);
        this.recommendations = this.recommendations.map((r) => {
          if (r.id === id) {
            return { ...r, is_dismissed: true, is_new: false };
          }
          return r;
        });
      } catch (err) {
        console.error("Не удалось скрыть вакансию", err);
        throw err;
      }
    },

    async markSeen(ids) {
      if (!ids || !ids.length) return;
      try {
        await axios.post("/api/recommendations/mark-seen/", { ids }, { headers: { "Content-Type": "application/json" } });
        const idSet = new Set(ids);
        this.recommendations = this.recommendations.map((r) =>
          idSet.has(r.id) ? { ...r, is_new: false } : r
        );
      } catch (err) {
        console.error("Не удалось отметить просмотренными", err);
      }
    },

    setMode(mode) {
      this.mode = mode;
    },

    setSelectedVariantId(variantId) {
      this.selectedVariantId = variantId;
    },

    setOnlyNew(value) {
      this.onlyNew = value;
    },
  },
});
