import { createRouter, createWebHistory } from 'vue-router'
import Login from '../views/Login.vue'
import Register from '../views/Register.vue'
import AdminDashboard from '../components/Admin/Dashboard.vue'
import UserDashboard from '../components/User/Dashboard.vue'
import LotSpots from '../components/Admin/LotSpots.vue'

const routes = [
  { path: '/', name: 'Login', component: Login },
  { path: '/register', name: 'Register', component: Register },
  { path: '/admin', name: 'AdminDashboard', component: AdminDashboard },
  { path: '/user', name: 'UserDashboard', component: UserDashboard },
  {
    path: '/admin/lot/:lot_id/spots',
    name: 'LotSpots',
    component: LotSpots,
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

export default router
