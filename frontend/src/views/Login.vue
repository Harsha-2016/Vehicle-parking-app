<template>
  <div class="container mt-5" style="max-width: 420px">
    <h3 class="text-center mb-4">Login</h3>

    <form @submit.prevent="loginUser">
      <div class="mb-3">
        <label class="form-label">Username</label>
        <input v-model="form.username" type="text" class="form-control" required />
      </div>

      <div class="mb-3">
        <label class="form-label">Password</label>
        <input v-model="form.password" type="password" class="form-control" required />
      </div>

      <div class="d-grid">
        <button class="btn btn-primary" type="submit" :disabled="loading">
          {{ loading ? 'Logging in…' : 'Login' }}
        </button>
      </div>
    </form>

    <p class="text-center mt-3">
      Don’t have an account?
      <router-link to="/register">Register here</router-link>
    </p>
  </div>
</template>

<script>
import API from '@/services/api'

export default {
  name: 'LoginView',
  data() {
    return {
      form: { username: '', password: '' },
      loading: false
    }
  },
  methods: {
    async loginUser() {
      try {
        this.loading = true
        const res = await API.post('/auth/login', this.form)
        const token = res.data.access_token || res.data.token
        const role = res.data.role
        localStorage.setItem('token', token)
        localStorage.setItem('role', role)
        localStorage.setItem("username", res.data.username);


        // Redirect based on role
        if (role === 'admin') {
          this.$router.push('/admin')
        } else {
          this.$router.push('/user')
        }
      } catch (err) {
        alert(err.response?.data?.error || 'Login failed')
      } finally {
        this.loading = false
      }
    }
  }
}
</script>
