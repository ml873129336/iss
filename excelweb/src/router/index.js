import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '../views/HomeView.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    // {
    //   path: '/',
    //   name: 'home',
    //   component: HomeView,
    // },
    {
      path: '/about',
      name: 'about',
      // route level code-splitting
      // this generates a separate chunk (About.[hash].js) for this route
      // which is lazy-loaded when the route is visited.
      component: () => import('../views/AboutView.vue'),
    },
    {
      path: '/upload',
      name: 'upload',
      // route level code-splitting
      // this generates a separate chunk (About.[hash].js) for this route
      // which is lazy-loaded when the route is visited.
      component: () => import('../components/upload.vue'),
    },
    {
      path: '/email',
      name: 'email',
      // route level code-splitting
      // this generates a separate chunk (About.[hash].js) for this route
      // which is lazy-loaded when the route is visited.
      component: () => import('../components/email.vue'),
    },
    {
      path: '/iss_fin',
      name: 'fin',
      // route level code-splitting
      // this generates a separate chunk (About.[hash].js) for this route
      // which is lazy-loaded when the route is visited.
      component: () => import('../components/\iss_fin.vue'),
    },
    {
      path: '/users',
      name: 'user',
      // route level code-splitting
      // this generates a separate chunk (About.[hash].js) for this route
      // which is lazy-loaded when the route is visited.
      component: () => import('../components/iss_user.vue'),
    },
    {
      path: '/asserts',
      name: 'assert',
      // route level code-splitting
      // this generates a separate chunk (About.[hash].js) for this route
      // which is lazy-loaded when the route is visited.
      component: () => import('../components/iss_assets.vue'),
    },

    {
      path: "/payment",
      name: "Payment",
      component: () => import('../components/iss_payment.vue'),
      meta: {
        title: "付款单生成",
      },
    },
    // {
    //   path: '/departments',
    //   name: 'department',
    //   // route level code-splitting
    //   // this generates a separate chunk (About.[hash].js) for this route
    //   // which is lazy-loaded when the route is visited.
    //   component: () => import('../components/\iss_fin.vue'),
    // },
    // {
    //   path: '/assets',
    //   name: 'assets',
    //   // route level code-splitting
    //   // this generates a separate chunk (About.[hash].js) for this route
    //   // which is lazy-loaded when the route is visited.
    //   component: () => import('../components/\iss_fin.vue'),
    // },
    // { path: '/', component: Dashboard },
    // { path: '/users', component: UserManagement },
    // { path: '/departments', component: DepartmentManagement },
    // { path: '/assets', component: AssetManagement },
  ],
})

export default router
