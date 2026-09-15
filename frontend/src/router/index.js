import { createRouter, createWebHistory } from "vue-router";
import BoardView from "../views/BoardView.vue";
import SearchView from "../views/SearchView.vue";

const routes = [
  { path: "/", name: "board", component: BoardView },
  { path: "/search", name: "search", component: SearchView },
];

export default createRouter({
  history: createWebHistory(),
  routes,
});
