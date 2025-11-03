<template>
  <div class="users-container">
    <h1 class="page-title">Registered Users</h1>

    <div class="table-wrapper">
      <table class="users-table">
        <thead>
          <tr>
            <th>ID</th>
            <th>Username</th>
            <th>Email</th>
            <th>Active Spot</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="user in users" :key="user.id">
            <td>{{ user.id }}</td>
            <td>{{ user.username }}</td>
            <td>{{ user.email }}</td>
            <td>
              <span v-if="user.active_spot" class="active">{{ user.active_spot }}</span>
              <span v-else class="inactive">None</span>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <p v-if="users.length === 0" class="no-users">No users found.</p>
  </div>
</template>

<script>
import axios from "axios";

export default {
  name: "Users",
  data() {
    return { users: [] };
  },
  async mounted() {
    try {
      const token = localStorage.getItem("token");
      const res = await axios.get("http://127.0.0.1:5000/admin/users", {
        headers: { Authorization: `Bearer ${token}` },
      });
      this.users = res.data;
      console.log("✅ Users fetched successfully:", this.users);
    } catch (err) {
      console.error("❌ Failed to fetch users:", err);
    }
  },
};
</script>

<style scoped>
.users-container {
  padding: 40px;
  background-color: #f5f7fa;
  min-height: 100vh;
}

.page-title {
  font-size: 1.8rem;
  font-weight: 600;
  color: #2c3e50;
  margin-bottom: 25px;
}

.table-wrapper {
  overflow-x: auto;
  background: white;
  border-radius: 10px;
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.08);
}

.users-table {
  width: 100%;
  border-collapse: collapse;
  text-align: left;
}

.users-table th,
.users-table td {
  padding: 14px 18px;
  border-bottom: 1px solid #eee;
}

.users-table th {
  background-color: #007bff;
  color: white;
  font-weight: 600;
}

.users-table tr:hover {
  background-color: #f1f5ff;
}

.active {
  color: #28a745;
  font-weight: 600;
}

.inactive {
  color: #dc3545;
  font-weight: 600;
}

.no-users {
  text-align: center;
  color: #6c757d;
  margin-top: 20px;
  font-size: 1.1rem;
}
</style>
