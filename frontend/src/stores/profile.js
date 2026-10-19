import { defineStore } from "pinia";
import axios from "axios";

export const useProfileStore = defineStore("profile", {
  state: () => ({
    profile: null,
    skills: [],
    workExperiences: [],
    education: [],
    variants: [],
    resumeFiles: [],
    isLoading: false,
    error: null,
    skillsLoading: false,
  }),

  actions: {
    async fetchProfile() {
      this.isLoading = true;
      this.error = null;
      try {
        const [profileRes, resumesRes] = await Promise.all([
          axios.get("/api/profile/"),
          axios.get("/api/profile/resumes/"),
        ]);
        this.profile = profileRes.data;
        this.workExperiences = profileRes.data.experiences || [];
        this.education = profileRes.data.education || [];
        this.variants = profileRes.data.variants || [];
        this.skills = profileRes.data.skills || [];
        this.resumeFiles = resumesRes.data || [];
      } catch (err) {
        this.error = "Не удалось загрузить профиль";
        console.error(err);
      } finally {
        this.isLoading = false;
      }
    },

    async updateProfile(data) {
      this.isLoading = true;
      this.error = null;
      try {
        const response = await axios.patch("/api/profile/", data);
        this.profile = response.data;
        this.workExperiences = response.data.experiences || [];
        this.education = response.data.education || [];
        this.variants = response.data.variants || [];
        this.skills = response.data.skills || [];
        return response.data;
      } catch (err) {
        this.error = "Не удалось обновить профиль";
        console.error(err);
        throw err;
      } finally {
        this.isLoading = false;
      }
    },

    async fetchWorkExperiences() {
      try {
        const response = await axios.get("/api/profile/experiences/");
        this.workExperiences = response.data || [];
        return response.data;
      } catch (err) {
        console.error("Не удалось загрузить опыт работы", err);
        return [];
      }
    },

    async fetchEducation() {
      try {
        const response = await axios.get("/api/profile/education/");
        this.education = response.data || [];
        return response.data;
      } catch (err) {
        console.error("Не удалось загрузить образование", err);
        return [];
      }
    },

    async fetchVariants() {
      try {
        const response = await axios.get("/api/profile/variants/");
        this.variants = response.data || [];
        return response.data;
      } catch (err) {
        console.error("Не удалось загрузить варианты профиля", err);
        return [];
      }
    },

    async fetchResumeFiles() {
      try {
        const response = await axios.get("/api/profile/resumes/");
        this.resumeFiles = response.data || [];
        return response.data;
      } catch (err) {
        console.error("Не удалось загрузить файлы резюме", err);
        return [];
      }
    },

    async fetchSkills(query = "") {
      this.skillsLoading = true;
      try {
        const response = await axios.get("/api/skills/", {
          params: { q: query },
        });
        return response.data;
      } catch (err) {
        console.error("Не удалось загрузить навыки", err);
        return [];
      } finally {
        this.skillsLoading = false;
      }
    },

    async createWorkExperience(data) {
      try {
        const response = await axios.post("/api/profile/experiences/", data);
        this.workExperiences.push(response.data);
        return response.data;
      } catch (err) {
        console.error("Не удалось создать запись опыта работы", err);
        throw err;
      }
    },

    async updateWorkExperience(id, data) {
      try {
        const response = await axios.patch("/api/profile/experiences/" + id + "/", data);
        const index = this.workExperiences.findIndex((e) => e.id === id);
        if (index !== -1) {
          this.workExperiences[index] = response.data;
        }
        return response.data;
      } catch (err) {
        console.error("Не удалось обновить опыт работы", err);
        throw err;
      }
    },

    async deleteWorkExperience(id) {
      try {
        await axios.delete("/api/profile/experiences/" + id + "/");
        this.workExperiences = this.workExperiences.filter((e) => e.id !== id);
      } catch (err) {
        console.error("Не удалось удалить опыт работы", err);
        throw err;
      }
    },

    async createEducation(data) {
      try {
        const response = await axios.post("/api/profile/education/", data);
        this.education.push(response.data);
        return response.data;
      } catch (err) {
        console.error("Не удалось создать запись об образовании", err);
        throw err;
      }
    },

    async updateEducation(id, data) {
      try {
        const response = await axios.patch("/api/profile/education/" + id + "/", data);
        const index = this.education.findIndex((e) => e.id === id);
        if (index !== -1) {
          this.education[index] = response.data;
        }
        return response.data;
      } catch (err) {
        console.error("Не удалось обновить образование", err);
        throw err;
      }
    },

    async deleteEducation(id) {
      try {
        await axios.delete("/api/profile/education/" + id + "/");
        this.education = this.education.filter((e) => e.id !== id);
      } catch (err) {
        console.error("Не удалось удалить образование", err);
        throw err;
      }
    },

    async createVariant(data) {
      try {
        const response = await axios.post("/api/profile/variants/", data);
        this.variants.push(response.data);
        return response.data;
      } catch (err) {
        console.error("Не удалось создать вариант профиля", err);
        throw err;
      }
    },

    async updateVariant(id, data) {
      try {
        const response = await axios.patch("/api/profile/variants/" + id + "/", data);
        const index = this.variants.findIndex((v) => v.id === id);
        if (index !== -1) {
          this.variants[index] = response.data;
        }
        return response.data;
      } catch (err) {
        console.error("Не удалось обновить вариант профиля", err);
        throw err;
      }
    },

    async deleteVariant(id) {
      try {
        await axios.delete("/api/profile/variants/" + id + "/");
        this.variants = this.variants.filter((v) => v.id !== id);
      } catch (err) {
        console.error("Не удалось удалить вариант профиля", err);
        throw err;
      }
    },

    async uploadResume(file, variantId = null) {
      const formData = new FormData();
      formData.append("file", file);
      if (variantId) {
        formData.append("variant", variantId);
      }
      try {
        const response = await axios.post("/api/profile/resumes/", formData, {
          headers: { "Content-Type": "multipart/form-data" },
        });
        this.resumeFiles.unshift(response.data);
        return response.data;
      } catch (err) {
        console.error("Не удалось загрузить резюме", err);
        throw err;
      }
    },

    async deleteResumeFile(id) {
      try {
        await axios.delete("/api/profile/resumes/" + id + "/");
        this.resumeFiles = this.resumeFiles.filter((r) => r.id !== id);
      } catch (err) {
        console.error("Не удалось удалить файл резюме", err);
        throw err;
      }
    },

    async downloadResumeFile(id) {
      try {
        const response = await axios.get("/api/profile/resumes/" + id + "/", {
          responseType: "blob",
        });
        const url = window.URL.createObjectURL(new Blob([response.data]));
        const link = document.createElement("a");
        link.href = url;
        const file = this.resumeFiles.find((r) => r.id === id);
        link.setAttribute("download", file?.original_name || "resume");
        document.body.appendChild(link);
        link.click();
        link.remove();
        window.URL.revokeObjectURL(url);
      } catch (err) {
        console.error("Не удалось скачать резюме", err);
        throw err;
      }
    },

    clearProfile() {
      this.profile = null;
      this.skills = [];
      this.workExperiences = [];
      this.education = [];
      this.variants = [];
      this.resumeFiles = [];
    },
  },
});