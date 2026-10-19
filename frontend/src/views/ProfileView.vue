<script setup>
import { onMounted, ref } from 'vue'
import { useAuthStore } from '../stores/auth'
import { useProfileStore } from '../stores/profile'
import { useRouter } from 'vue-router'

import ProfileBasicInfo from '../components/profile/ProfileBasicInfo.vue'
import ProfileSkills from '../components/profile/ProfileSkills.vue'
import ProfileWorkExperience from '../components/profile/ProfileWorkExperience.vue'
import ProfileEducation from '../components/profile/ProfileEducation.vue'
import ProfileVariants from '../components/profile/ProfileVariants.vue'
import ProfileResumes from '../components/profile/ProfileResumes.vue'

const authStore = useAuthStore()
const profileStore = useProfileStore()
const router = useRouter()

const isLoading = ref(false)

async function loadProfile() {
  isLoading.value = true
  try {
    await Promise.all([
      profileStore.fetchProfile(),
      profileStore.fetchWorkExperiences(),
      profileStore.fetchEducation(),
      profileStore.fetchVariants(),
      profileStore.fetchResumeFiles(),
    ])
  } catch (err) {
    console.error('Failed to load profile', err)
  } finally {
    isLoading.value = false
  }
}

function handleLogout() {
  authStore.logout()
  profileStore.clearProfile()
  router.push('/login')
}

onMounted(() => {
  if (!authStore.user) {
    authStore.fetchMe().then(() => {
      loadProfile()
    })
  } else {
    loadProfile()
  }
})
</script>

<template>
  <div class="profile-page">
    <div class="profile-header">
      <h1 class="page-title">Профиль</h1>
      <button class="logout-button" @click="handleLogout">Выйти</button>
    </div>

    <div v-if="isLoading" class="loading-state">
      <div class="spinner"></div>
      <p>Загрузка профиля...</p>
    </div>

    <div v-else class="profile-grid">
      <div class="profile-col profile-col-wide">
        <ProfileBasicInfo
          :profile="profileStore.profile"
          @update="profileStore.fetchProfile"
        />
        <ProfileSkills
          :skills="profileStore.profile?.skills || []"
          @update="profileStore.fetchProfile"
        />
      </div>

      <div class="profile-col">
        <ProfileWorkExperience
          :experiences="profileStore.workExperiences"
          @update="profileStore.fetchWorkExperiences"
        />
        <ProfileEducation
          :education="profileStore.education"
          @update="profileStore.fetchEducation"
        />
        <ProfileVariants
          :variants="profileStore.variants"
          :all-skills="profileStore.profile?.skills || []"
          :all-experiences="profileStore.workExperiences"
          @update="profileStore.fetchVariants"
        />
        <ProfileResumes
          :resume-files="profileStore.resumeFiles"
          :variants="profileStore.variants"
          @update="profileStore.fetchResumeFiles"
        />
      </div>
    </div>
  </div>
</template>

<style scoped>
.profile-page {
  padding: 24px;
  max-width: 1080px;
  margin: 0 auto;
}

.profile-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}

.page-title {
  font-size: 28px;
  font-weight: 700;
  color: #1a1a1a;
  margin: 0;
}

.logout-button {
  background: transparent;
  border: 1px solid #ddd;
  color: #555;
  font-size: 14px;
  font-weight: 600;
  padding: 10px 20px;
  border-radius: 10px;
  cursor: pointer;
  transition: all 0.2s;
}

.logout-button:hover {
  background: #f4f5f7;
  color: #1a1a1a;
  border-color: #ccc;
}

.loading-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 60px 20px;
  color: #888;
}

.spinner {
  width: 32px;
  height: 32px;
  border: 3px solid #eef0f5;
  border-top-color: #4a6cf7;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
  margin-bottom: 16px;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.profile-grid {
  display: grid;
  grid-template-columns: 2fr 1fr;
  gap: 24px;
}

.profile-col-wide {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.profile-col {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

@media (max-width: 900px) {
  .profile-grid {
    grid-template-columns: 1fr;
  }
}
</style>