import { defineStore } from "pinia";
import axios from "axios";

export const useApplicationStore = defineStore("applications", {
  state: () => ({
    applications: [],
    isLoading: false,
    error: null,
  }),

  getters: {
    likedVacancyIds: (state) =>
      new Set(state.applications.map((app) => app.vacancy.id)),
  },

  actions: {
    async fetchApplications() {
      this.isLoading = true;
      this.error = null;
      try {
        const response = await axios.get("/api/applications/");
        this.applications = response.data;
      } catch (err) {
        this.error = "Не удалось загрузить отклики";
        console.error(err);
      } finally {
        this.isLoading = false;
      }
    },

    async updateStatus(applicationId, newStatus) {
      const application = this.applications.find((a) => a.id === applicationId);
      if (!application) return;

      const previousStatus = application.status;
      application.status = newStatus;

      try {
        await axios.patch(`/api/applications/${applicationId}/`, {
          status: newStatus,
        });
      } catch (err) {
        application.status = previousStatus;
        console.error("Не удалось обновить статус, откатили изменение", err);
      }
    },

    async createApplicationFromVacancy(vacancyId) {
      try {
        const response = await axios.post("/api/applications/", {
          vacancy_id: vacancyId,
          status: "found",
        });
        const alreadyExists = this.applications.some(
          (app) => app.id === response.data.id,
        );
        if (!alreadyExists) {
          this.applications.push(response.data);
        }
        return true;
      } catch (err) {
        console.error("Не удалось добавить вакансию в отклики", err);
        return false;
      }
    },

    async updateNotes(applicationId, notes) {
      try {
        const response = await axios.patch(
          `/api/applications/${applicationId}/`,
          { notes },
        );
        const index = this.applications.findIndex(
          (a) => a.id === applicationId,
        );
        if (index !== -1) {
          this.applications[index] = response.data;
        }
        return true;
      } catch (err) {
        console.error("Не удалось сохранить заметку", err);
        return false;
      }
    },
    async removeApplication(applicationId) {
      try {
        await axios.delete(`/api/applications/${applicationId}/`);
        this.applications = this.applications.filter(
          (app) => app.id !== applicationId,
        );
        return true;
      } catch (err) {
        console.error("Не удалось удалить вакансию из отслеживаемых", err);
        return false;
      }
    },
  },
});
