<template>
  <div class="analytics-container">
    <h3 class="text-center mb-4">📊 Parking Analytics Dashboard</h3>

    <!-- Revenue Summary Chart -->
    <div class="chart-section">
      <h5>Total Revenue by Lot</h5>
      <canvas id="revenueChart"></canvas>
    </div>

    <!-- Parking Activity Chart -->
    <div class="chart-section">
      <h5>Parking Activity (Reservations per Lot)</h5>
      <canvas id="activityChart"></canvas>
    </div>

    <!-- Overall Stats -->
    <div class="summary-cards">
      <div class="card">
        <h4>{{ totalRevenue }}</h4>
        <p>Total Revenue (₹)</p>
      </div>
      <div class="card">
        <h4>{{ totalReservations }}</h4>
        <p>Total Reservations</p>
      </div>
    </div>
  </div>
</template>

<script>
import axios from "axios";
import Chart from "chart.js/auto";

export default {
  name: "AdminAnalytics",
  data() {
    return {
      totalRevenue: 0,
      totalReservations: 0,
      revenueChart: null,
      activityChart: null,
    };
  },
  async mounted() {
    const token = localStorage.getItem("token");
    try {
      // Fetch analytics data
      const res = await axios.get("http://127.0.0.1:5000/admin/analytics", {
        headers: { Authorization: `Bearer ${token}` },
      });

      const data = res.data;

      // --- Extract values ---
      const lotNames = data.map((d) => d.lot_name);
      const revenues = data.map((d) => d.total_revenue);
      const reservations = data.map((d) => d.total_reservations);

      // Compute totals
      this.totalRevenue = revenues.reduce((a, b) => a + b, 0);
      this.totalReservations = reservations.reduce((a, b) => a + b, 0);

      // --- Render Charts ---
      this.renderRevenueChart(lotNames, revenues);
      this.renderActivityChart(lotNames, reservations);
    } catch (err) {
      console.error("Error loading analytics:", err);
    }
  },
  methods: {
    renderRevenueChart(labels, data) {
      const ctx = document.getElementById("revenueChart").getContext("2d");
      if (this.revenueChart) this.revenueChart.destroy();
      this.revenueChart = new Chart(ctx, {
        type: "bar",
        data: {
          labels,
          datasets: [
            {
              label: "Revenue (₹)",
              data,
              backgroundColor: "#007bffaa",
            },
          ],
        },
        options: {
          responsive: true,
          scales: {
            y: { beginAtZero: true },
          },
        },
      });
    },
    renderActivityChart(labels, data) {
      const ctx = document.getElementById("activityChart").getContext("2d");
      if (this.activityChart) this.activityChart.destroy();
      this.activityChart = new Chart(ctx, {
        type: "line",
        data: {
          labels,
          datasets: [
            {
              label: "Reservations",
              data,
              borderColor: "#28a745",
              backgroundColor: "#28a74533",
              fill: true,
              tension: 0.3,
            },
          ],
        },
        options: {
          responsive: true,
          scales: {
            y: { beginAtZero: true },
          },
        },
      });
    },
  },
};
</script>

<style scoped>
.analytics-container {
  padding: 30px;
  background: #fafafa;
  border-radius: 12px;
  box-shadow: 0 3px 10px rgba(0, 0, 0, 0.05);
}

.chart-section {
  background: white;
  border-radius: 10px;
  padding: 20px;
  margin-bottom: 40px;
  box-shadow: 0 3px 8px rgba(0, 0, 0, 0.1);
}

.summary-cards {
  display: flex;
  justify-content: center;
  gap: 30px;
  margin-top: 30px;
}

.card {
  background: #007bff;
  color: white;
  padding: 20px 30px;
  border-radius: 10px;
  width: 200px;
  text-align: center;
  box-shadow: 0 3px 8px rgba(0, 0, 0, 0.2);
  transition: transform 0.2s ease;
}

.card:hover {
  transform: translateY(-3px);
}

.card h4 {
  margin: 0;
  font-size: 1.8rem;
}

.card p {
  margin-top: 10px;
  font-weight: 500;
}
</style>
