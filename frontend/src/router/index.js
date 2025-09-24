import { createRouter, createWebHistory } from 'vue-router'
import NotePage from '../views/NotePage.vue'
import SettingsPage from '../views/SettingsPage.vue'
import TodoPage from '../views/TodoPage.vue'
import AIChatPage from '../views/AIChatPage.vue'
import PomodoroPage from '../views/PomodoroPage.vue'
import ProjectPage from '../views/ProjectPage.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'notes',
      component: NotePage
    },
    {
      path: '/settings',
      name: 'settings',
      component: SettingsPage
    },
    {
      path: '/todos',
      name: 'todos',
      component: TodoPage
    },
    {
      path: '/chat',
      name: 'chat',
      component: AIChatPage
    },
    {
      path: '/pomodoro',
      name: 'pomodoro',
      component: PomodoroPage
    },
    {
      path: '/projects',
      name: 'projects',
      component: ProjectPage
    }
  ]
})

export default router