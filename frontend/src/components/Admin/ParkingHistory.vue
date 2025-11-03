<template>
  <div class="history-container">
    <h3 class="text-center mb-4">🚗 Parking History</h3>

    <div v-if="records.length">
      <table class="table table-striped table-bordered shadow-sm">
        <thead class="table-dark">
          <tr>
            <th>User</th>
            <th>Lot</th>
            <th>Spot ID</th>
            <th>Start</th>
            <th>End</th>
            <th>Duration</th>
            <th>Cost (₹)</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="rec in records" :key="rec.reservation_id">
            <td>{{ rec.user_name }}</td>
            <td>{{ rec.lot_name }}</td>
            <td>{{ rec.spot_id }}</td>
            <td>{{ formatTimestamp(rec.parking_timestamp) }}</td>
            <td>{{ formatTimestamp(rec.leaving_timestamp) }}</td>
            <td>{{ rec.duration || '—' }}</td>
            <td>{{ rec.parking_cost || '—' }}</td>
          </tr>
        </tbody>
      </table>
    </div>

    <p v-else class="text-muted text-center">No parking records available.</p>
  </div>
</template>

<script>
import axios from "axios";

export default {
  name: "ParkingHistory",
  data() {
    return { records: [] };
  },
  methods: {
    async fetchHistory() {
      try {
        const token = localStorage.getItem("token");
        const res = await axios.get("http://127.0.0.1:5000/admin/reservations", {
          headers: { Authorization: `Bearer ${token}` },
        });
        this.records = res.data;
        console.log("Fetched reservations:", this.records);
      } catch (err) {
        console.error("Error fetching reservations:", err.response?.data || err.message);
      }
    },
    formatTimestamp(ts) {
      if (!ts) return "—";
      const date = new Date(ts);
      return date.toLocaleString();
    },
  },
  mounted() {
    this.fetchHistory();
  },
};
</script>

<style scoped>
.history-container {
  background: #ffffff;
  padding: 30px;
  border-radius: 12px;
  box-shadow: 0 3px 10px rgba(0, 0, 0, 0.05);
}

.table {
  width: 100%;
  border-radius: 10px;
  overflow: hidden;
}

.table th,
.table td {
  vertical-align: middle;
  text-align: center;
}

.table th {
  background-color: #007bff !important;
  color: white;
}

.table td {
  font-size: 0.95rem;
}

.text-muted {
  font-style: italic;
  font-size: 1rem;
}
</style>
