<template>
  <div class="spots-container">
    <h2>Parking Spots for Lot ID: {{ lotId }}</h2>

    <div v-if="loading" class="loading-text">Loading spots...</div>

    <div v-else>
      <table v-if="spots.length" class="spots-table">
        <thead>
          <tr>
            <th>Spot ID</th>
            <th>Status</th>
            <th>Username</th>
            <th>User ID</th>
            <th>Parking Timestamp</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="spot in spots" :key="spot.spot_id">
            <td>{{ spot.spot_id }}</td>
            <td>
              <span
                :class="{
                  'status-available': spot.status === 'available',
                  'status-occupied': spot.status === 'occupied'
                }"
              >
                {{ spot.status }}
              </span>
            </td>
            <td>{{ spot.user_details?.username || '-' }}</td>
            <td>{{ spot.user_details?.user_id || '-' }}</td>
            <td>
              {{
                spot.user_details?.parking_timestamp
                  ? formatTimestamp(spot.user_details.parking_timestamp)
                  : '-'
              }}
            </td>
          </tr>
        </tbody>
      </table>

      <p v-else class="no-data">No spots found for this parking lot.</p>

      <button class="btn-back" @click="$router.push('/admin/dashboard')">
        ← Back to Lots
      </button>
    </div>
  </div>
</template>

<script>
import axios from "axios";

export default {
  name: "LotSpots",
  data() {
    return {
      lotId: this.$route.params.lot_id,
      spots: [],
      loading: true,
    };
  },
  async mounted() {
    await this.fetchSpots();
  },
  methods: {
    async fetchSpots() {
      try {
        const token = localStorage.getItem("token");
        const response = await axios.get(
          `http://127.0.0.1:5000/admin/lot/${this.lotId}/spots`,
          {
            headers: { Authorization: `Bearer ${token}` },
          }
        );
        this.spots = response.data;
      } catch (err) {
        console.error("Error fetching spots:", err.response?.data || err.message);
      } finally {
        this.loading = false;
      }
    },
    formatTimestamp(ts) {
      const date = new Date(ts);
      return date.toLocaleString();
    },
  },
};
</script>

<style scoped>
.spots-container {
  max-width: 900px;
  margin: 40px auto;
  background: #f9fafc;
  border-radius: 12px;
  padding: 25px;
  box-shadow: 0 3px 10px rgba(0, 0, 0, 0.1);
}

h2 {
  text-align: center;
  margin-bottom: 25px;
  color: #333;
}

.loading-text {
  text-align: center;
  color: #666;
  font-style: italic;
}

.spots-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 15px;
  margin-bottom: 25px;
}

.spots-table th,
.spots-table td {
  padding: 10px;
  border: 1px solid #ddd;
  text-align: center;
}

.spots-table th {
  background-color: #007bff;
  color: white;
  font-weight: 600;
}

.status-available {
  color: green;
  font-weight: 600;
}
.status-occupied {
  color: red;
  font-weight: 600;
}

.no-data {
  text-align: center;
  color: #777;
  font-style: italic;
  margin: 20px 0;
}

.btn-back {
  background-color: #6c757d;
  color: white;
  border: none;
  padding: 10px 16px;
  border-radius: 8px;
  cursor: pointer;
  display: block;
  margin: 0 auto;
}
.btn-back:hover {
  background-color: #5a6268;
}
</style>
