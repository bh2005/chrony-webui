import { createApp } from 'vue'
import { createRouter, createWebHistory } from 'vue-router'
import App from './App.vue'
import Dashboard from './views/Dashboard.vue'
import Config from './views/Config.vue'
import LoginView from './views/LoginView.vue'
import { isLoggedIn } from './api.js'
import './style.css'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/',          redirect: '/dashboard' },
    { path: '/login',     component: LoginView,  meta: { public: true } },
    { path: '/dashboard', component: Dashboard,  meta: { public: true } },
    { path: '/config',    component: Config },
  ]
})

router.beforeEach((to) => {
  if (!to.meta.public && !isLoggedIn()) {
    return { path: '/login', query: { redirect: to.fullPath } }
  }
})

createApp(App).use(router).mount('#app')
