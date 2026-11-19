import { createRouter, createWebHashHistory } from 'vue-router'

const router = createRouter({
  history: createWebHashHistory(),
  routes: [
    {
      path: '/',
      component: () => import('src/layouts/MainLayout.vue'),
      children: [
        {
          path: '',
          component: () => import('src/pages/ChatPage.vue')
        }
      ]
    }
  ]
})

export default router
