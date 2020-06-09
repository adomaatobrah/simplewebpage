import Vue from 'vue';
import Router from 'vue-router';
import Ping from './components/Ping.vue';

Vue.use(Router);

const router = new Router({
  mode: 'history',
  base: process.env.BASE_URL,
  routes: [
    {
      path: '/',
      redirect: '/ping',
    },
    {
      path: '/ping',
      name: 'Ping',
      component: Ping,
    },
  ],
});

export default router;
