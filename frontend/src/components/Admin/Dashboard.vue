<template>
  <div class="dashboard-container">
    <div class="d-flex justify-content-between align-items-center mb-4">
      <h2>👋 Welcome, {{ username || 'Admin' }}</h2>
      <button class="btn btn-danger btn-sm" @click="logout">Logout</button>
    </div>

    <!-- Stats Cards -->
    <div class="stats-container">
      <div class="stat-card">
        <h2>{{ lotCount }}</h2>
        <p>Total Parking Lots</p>
      </div>
      <div class="stat-card">
        <h2>{{ userCount }}</h2>
        <p>Registered Users</p>
      </div>
    </div>

    <!-- Tabs -->
    <div class="tabs">
      <button
        :class="['tab', activeTab === 'lots' ? 'active' : '']"
        @click="activeTab = 'lots'"
      >
        Manage Lots
      </button>
      <button
        :class="['tab', activeTab === 'users' ? 'active' : '']"
        @click="activeTab = 'users'"
      >
        View Users
      </button>
      <button
        :class="['tab', activeTab === 'history' ? 'active' : '']"
        @click="activeTab = 'history'"
      >
        Parking History
      </button>
      <button
        :class="['tab', activeTab === 'analytics' ? 'active' : '']"
        @click="activeTab = 'analytics'"
      >
        Analytics
      </button>
    </div>

    <!-- Tab Content -->
    <div class="tab-content">
      <Lots v-if="activeTab === 'lots'" />
      <Users v-if="activeTab === 'users'" />
      <div v-if="activeTab === 'history'" class="history-section">
        <ParkingHistory />

        <div class="export-container">
          <button class="btn btn-success" @click="downloadCSV">
            ⬇️ Export Reservation History (CSV)
          </button>
        </div>
      </div>
      <AdminAnalytics v-if="activeTab === 'analytics'" />
    </div>
  </div>
</template>

<script>
import axios from "axios";
import Lots from "./Lots.vue";
import Users from "./Users.vue";
import ParkingHistory from "./ParkingHistory.vue";
import AdminAnalytics from "./AdminAnalytics.vue";

export default {
  name: "Dashboard",
  components: { Lots, Users, ParkingHistory, AdminAnalytics },
  data() {
    return {
      lotCount: 0,
      userCount: 0,
      activeTab: "lots",
      username: localStorage.getItem("username"),
    };
  },
  async mounted() {
    const token = localStorage.getItem("token");
    try {
      const [lotsRes, usersRes] = await Promise.all([
        axios.get("http://127.0.0.1:5000/admin/lots", {
          headers: { Authorization: `Bearer ${token}` },
        }),
        axios.get("http://127.0.0.1:5000/admin/users", {
          headers: { Authorization: `Bearer ${token}` },
        }),
      ]);
      this.lotCount = lotsRes.data.length;
      this.userCount = usersRes.data.length;
    } catch (err) {
      console.error("Error fetching data:", err.message);
    }
  },
  methods: {
    logout() {
      localStorage.removeItem("token");
      localStorage.removeItem("role");
      localStorage.removeItem("username");
      alert("You have been logged out.");
      this.$router.push("/");
    },
    async downloadCSV() {
      
      const token = localStorage.getItem("token");
      try {
        const response = await axios.get(
            "http://127.0.0.1:5000/admin/export-history",
          {
            headers: { Authorization: `Bearer ${token}` },
          } 
          );

        // ✅ The server now sends a simple success message (not a file)
        alert(response.data.message || "✅ Export started! You’ll get the file soon.");
      } catch (err) {
          console.error("Error exporting CSV:", err.response?.data || err.message);
          alert("❌ Failed to start export.");
    }
  },
},
};
</script>

<style scoped>
.dashboard-container {
  padding: 40px;
  text-align: center;
}

.stats-container {
  display: flex;
  justify-content: center;
  gap: 30px;
  margin: 30px 0;
}

.stat-card {
  background: #007bff;
  color: white;
  padding: 25px;
  width: 200px;
  border-radius: 12px;
  box-shadow: 0 3px 10px rgba(0, 0, 0, 0.2);
  transition: transform 0.2s ease;
}
.stat-card:hover {
  transform: translateY(-4px);
}

.tabs {
  display: flex;
  justify-content: center;
  margin-top: 30px;
  gap: 10px;
}
.tab {
  background: #eaeaea;
  border: none;
  padding: 10px 20px;
  border-radius: 8px;
  cursor: pointer;
  font-weight: 600;
  transition: background 0.2s ease;
}
.tab.active {
  background: #007bff;
  color: white;
}
.tab:hover {
  background: #d0d0d0;
}

.tab-content {
  margin-top: 40px;
  background: #fafafa;
  padding: 30px;
  border-radius: 12px;
  box-shadow: 0 3px 10px rgba(0, 0, 0, 0.05);
}

.export-container {
  margin-top: 30px;
}
.btn-success {
  background-color: #28a745;
  border: none;
  padding: 10px 20px;
  font-weight: bold;
  border-radius: 8px;
  color: white;
  transition: background 0.3s ease;
}
.btn-success:hover {
  background-color: #218838;
}
</style>
