import { createRouter, createWebHistory } from "vue-router";
import BoardView from "../views/BoardView.vue";
import SearchView from "../views/SearchView.vue";
import LoginView from "../views/LoginView.vue";
import RegisterView from "../views/RegisterView.vue";
import ProfileView from "../views/ProfileView.vue";
import { useAuthStore } from "../stores/auth";

const routes = [
  {
    path: "/",
    name: "board",
    component: BoardView,
    meta: { requiresAuth: true },
  },
  {
    path: "/search",
    name: "search",
    component: SearchView,
    meta: { requiresAuth: true },
  },
  {
    path: "/profile",
    name: "profile",
    component: ProfileView,
    meta: { requiresAuth: true },
  },
  { path: "/login", name: "login", component: LoginView },
  { path: "/register", name: "register", component: RegisterView },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

router.beforeEach((to) => {
  const authStore = useAuthStore();
  if (to.meta.requiresAuth && !authStore.isAuthenticated) {
    return { name: "login" };
  }
});

export default router;
