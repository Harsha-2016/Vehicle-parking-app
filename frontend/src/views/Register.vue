<template>
  <div class="container mt-5" style="max-width: 420px">
    <h3 class="text-center mb-4">Register</h3>

    <form @submit.prevent="registerUser">
      <div class="mb-3">
        <label class="form-label">Username</label>
        <input v-model="form.username" type="text" class="form-control" required />
      </div>

      <div class="mb-3">
        <label class="form-label">Email</label>
        <input v-model="form.email" type="email" class="form-control" required />
      </div>

      <div class="mb-3">
        <label class="form-label">Password</label>
        <input v-model="form.password" type="password" class="form-control" required />
      </div>

      <div class="d-grid">
        <button class="btn btn-success" type="submit" :disabled="loading">
          {{ loading ? 'Registering…' : 'Register' }}
        </button>
      </div>
    </form>

    <p class="text-center mt-3">
      Already have an account?
      <router-link to="/login">Login here</router-link>
    </p>
  </div>
</template>

<script>

import API from '@/services/api'

export default {
  name: 'RegisterView',
  data() {
    return {
      form: { username: '', email: '', password: '' },
      loading: false,
      error: ''
    }
  },
  methods: {
    async registerUser() {
      this.loading = true;
      this.error = '';

      try {
        const res = await API.post('/auth/register', this.form)

        if (res.status === 201) {
          alert('✅ Registration successful! Redirecting to login...');
          this.$router.push('/');
        }
      } catch (err) {
        console.error('Registration failed:', err);
        this.error = err.response?.data?.error || 'Registration failed. Please try again.';
        alert(this.error);
      } finally {
        this.loading = false;
      }
    }
  }
}
</script>

<style scoped>
.container {
  margin-top: 60px;
}
</style>
