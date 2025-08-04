import Home from '@/views/HomeView.vue'
import dataView from '@/views/os-data-View.vue'
import estado from '@/views/estado-data-View.vue'
import Login from '@/views/LoginView.vue'
import Vue from 'vue'
import Cookies from 'js-cookie'
import VueRouter from 'vue-router'
import store from '@/store'

Vue.use(VueRouter)

const routes = [
  {
    path: '/',
    component: Home
  },
  {
    path: '/page1',
    component: dataView,
    meta: { requiresAuth: true }
  },
  {
    path: '/page2',
    component: estado,
    meta: { requiresAuth: true }
  },
  {
    path: '/login',
    component: Login
  }
]

const router = new VueRouter({
  mode: 'history',
  routes
})

router.beforeEach((to, from, next) => {
  try{
    const token = Cookies.get('token')
    if(token == null){ throw new Error('token inexistente');}
    store.commit('logar',token)
  }catch(erro){
    store.commit('logout')
  }
  if (to.matched.some(record => record.meta.requiresAuth)) {
    if (!store.getters.logado) {
      next('/login');
    } else {
      next();
    }
  } else {
    next();
  }
});

export default router
