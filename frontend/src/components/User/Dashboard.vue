<template>
  <div class="container py-4">
    <h2 class="text-center mb-4">User Dashboard</h2>
    <div class="d-flex justify-content-between align-items-center mb-4">
      <h5>👋 Welcome, {{ username || 'User' }}</h5>
      <button class="btn btn-danger btn-sm" @click="logout">Logout</button>
    </div>

    <!-- Available Lots Section -->
    <section class="mb-5">
      <h4 class="mb-3">Available Parking Lots</h4>
      <div v-if="lots.length" class="row">
        <div v-for="lot in lots" :key="lot.lot_id" class="col-md-4 mb-3">
          <div class="card shadow-sm h-100">
            <div class="card-body">
              <h5 class="card-title">{{ lot.prime_location_name }}</h5>
              <p class="card-text mb-1"><strong>Address:</strong> {{ lot.address }}</p>
              <p class="card-text mb-1"><strong>Pin Code:</strong> {{ lot.pin_code }}</p>
              <p class="card-text mb-1">
                <strong>Spots:</strong> {{ lot.available_spots }} / {{ lot.total_spots }}
              </p>
              <p class="card-text mb-3"><strong>Price/hour:</strong> ₹{{ lot.price }}</p>

              <button
                class="btn btn-primary w-100"
                :disabled="lot.available_spots === 0 || activeReservation"
                @click="reserveSpot(lot.lot_id)"
              >
                {{ lot.available_spots === 0 ? 'Full' : 'Reserve Spot' }}
              </button>
            </div>
          </div>
        </div>
      </div>
      <p v-else class="text-muted">No parking lots available.</p>
    </section>

    <hr />

    <!-- Active Reservation -->
    <section class="mb-5" v-if="activeReservation">
      <h4 class="mb-3">Your Active Reservation</h4>
      <div class="card border-success shadow-sm">
        <div class="card-body">
          <h5 class="card-title">Lot: {{ activeReservation.lot_name }}</h5>
          <p class="card-text mb-1"><strong>Spot ID:</strong> {{ activeReservation.spot_id }}</p>
          <p class="card-text mb-1">
            <strong>Start Time:</strong>
            {{ formatTimestamp(activeReservation.parking_timestamp) }}
          </p>
          <button
            class="btn btn-danger mt-2"
            @click="releaseSpot(activeReservation.reservation_id)"
          >
            Release Spot
          </button>
        </div>
      </div>
    </section>

    <section v-else class="text-muted mb-5">
      <h4>Your Active Reservation</h4>
      <p>No active reservation currently.</p>
    </section>

    <hr />

    <!-- Reservation History -->
    <section>
      <h4 class="mb-3">Reservation History</h4>
      <div v-if="pastReservations.length">
        <table class="table table-striped table-bordered">
          <thead class="table-dark">
            <tr>
              <th>Lot Name</th>
              <th>Spot ID</th>
              <th>Start</th>
              <th>End</th>
              <th>Cost (₹)</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="res in pastReservations" :key="res.reservation_id">
              <td>{{ res.lot_name }}</td>
              <td>{{ res.spot_id }}</td>
              <td>{{ formatTimestamp(res.parking_timestamp) }}</td>
              <td>{{ formatTimestamp(res.leaving_timestamp) }}</td>
              <td>{{ res.parking_cost }}</td>
            </tr>
          </tbody>
        </table>
      </div>
      <p v-else class="text-muted">No past reservations yet.</p>
    </section>
  </div>
</template>

<script>
import axios from "axios";

export default {
  name: "UserDashboard",
  data() {
    return {
      lots: [],
      activeReservation: null,
      pastReservations: [],
      loading: false,
      username: localStorage.getItem("username") || null,
    };
  },
  methods: {
    async fetchLots() {
      try {
        const token = localStorage.getItem("token");
        const res = await axios.get("http://127.0.0.1:5000/user/lots", {
          headers: { Authorization: `Bearer ${token}` },
        });
        this.lots = res.data;
      } catch (err) {
        console.error("Error fetching lots:", err.response?.data || err.message);
      }
    },

    async fetchReservations() {
      try {
        const token = localStorage.getItem("token");
        const res = await axios.get("http://127.0.0.1:5000/user/me/reservations", {
          headers: { Authorization: `Bearer ${token}` },
        });

        const all = res.data;
        this.activeReservation = all.find(r => !r.leaving_timestamp) || null;
        this.pastReservations = all.filter(r => r.leaving_timestamp);
      } catch (err) {
        console.error("Error fetching reservations:", err.response?.data || err.message);
      }
    },

    async reserveSpot(lotId) {
      if (!confirm("Reserve a spot in this lot?")) return;

      try {
        const token = localStorage.getItem("token");
        const res = await axios.post(
          "http://127.0.0.1:5000/user/reserve",
          { lot_id: lotId },
          { headers: { Authorization: `Bearer ${token}` } }
        );

        alert("✅ Spot reserved successfully!");
        await this.fetchLots();
        await this.fetchReservations();
      } catch (err) {
        alert(err.response?.data?.error || "Reservation failed");
      }
    },

    async releaseSpot(reservationId) {
      if (!confirm("Release this spot?")) return;

      try {
         console.log("DEBUG Sending reservation_id:", reservationId);
        const token = localStorage.getItem("token");
        const res = await axios.post(
          "http://127.0.0.1:5000/user/release",
          { reservation_id: reservationId },
          { headers: { Authorization: `Bearer ${token}` } }
        );

        alert(`✅ Spot released! Cost: ₹${res.data.parking_cost}`);
        await this.fetchLots();
        await this.fetchReservations();
      } catch (err) {
        alert(err.response?.data?.error || "Release failed");
      }
    },

    formatTimestamp(ts) {
      if (!ts) return "—";
    // Ensure the backend UTC timestamp is treated as UTC
    const date = new Date(ts + "Z");
    return date.toLocaleString(); // Converts automatically to your local (IST) timezone
    },
    logout() {
      localStorage.removeItem("token");
      localStorage.removeItem("role");
      localStorage.removeItem("username");
      alert("You have been logged out.");
      this.$router.push("/");
    },
  },
  async mounted() {
    await this.fetchLots();
    await this.fetchReservations();
  },
};
</script>

<style scoped>
.card {
  border-radius: 12px;
}
.card-title {
  color: #007bff;
}
section {
  margin-bottom: 40px;
}
hr {
  margin: 40px 0;
}
</style>
