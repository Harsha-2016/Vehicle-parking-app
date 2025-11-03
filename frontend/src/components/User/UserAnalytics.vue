<template>
  <div class="analytics-container">
    <h2 class="analytics-title">📊 Your Parking Analytics</h2>

    <!-- Summary Cards -->
    <div class="summary-container">
      <div class="summary-card">
        <h3>{{ totalHours }} hrs</h3>
        <p>Total Hours Parked</p>
      </div>
      <div class="summary-card">
        <h3>₹{{ totalSpent }}</h3>
        <p>Total Amount Spent</p>
      </div>
    </div>

    <!-- Charts -->
    <div class="chart-container">
      <canvas id="userParkingChart"></canvas>
    </div>

    <div class="chart-container">
      <canvas id="userRevenueChart"></canvas>
    </div>
  </div>
</template>

<script>
import axios from "axios";
import Chart from "chart.js/auto";

export default {
  name: "UserAnalytics",
  data() {
    return {
      parkingChart: null,
      revenueChart: null,
      totalHours: 0,
      totalSpent: 0,
    };
  },
  mounted() {
    this.fetchUserAnalytics();
  },
  methods: {
    async fetchUserAnalytics() {
      try {
        const token = localStorage.getItem("token");
        const res = await axios.get("http://127.0.0.1:5000/user/analytics", {
          headers: { Authorization: `Bearer ${token}` },
        });

        const data = res.data;

        // update summary cards
        this.totalHours = data.total_hours || 0;
        this.totalSpent = data.total_spent || 0;

        // prepare chart data
        const months = data.parkingStats.map((x) => x.month);
        const hours = data.parkingStats.map((x) => x.hours);
        const amounts = data.revenueStats.map((x) => x.amount);

        this.renderParkingChart(months, hours);
        this.renderRevenueChart(months, amounts);
      } catch (err) {
        console.error("Error fetching user analytics:", err);
      }
    },

    renderParkingChart(labels, data) {
      const ctx = document.getElementById("userParkingChart");
      if (this.parkingChart) this.parkingChart.destroy();

      this.parkingChart = new Chart(ctx, {
        type: "bar",
        data: {
          labels,
          datasets: [
            {
              label: "Hours Parked (per Month)",
              data,
              backgroundColor: "rgba(54, 162, 235, 0.6)",
              borderColor: "rgba(54, 162, 235, 1)",
              borderWidth: 1.5,
            },
          ],
        },
        options: { responsive: true, scales: { y: { beginAtZero: true } } },
      });
    },

    renderRevenueChart(labels, data) {
      const ctx = document.getElementById("userRevenueChart");
      if (this.revenueChart) this.revenueChart.destroy();

      this.revenueChart = new Chart(ctx, {
        type: "line",
        data: {
          labels,
          datasets: [
            {
              label: "Amount Spent (₹)",
              data,
              fill: true,
              backgroundColor: "rgba(255, 99, 132, 0.3)",
              borderColor: "rgba(255, 99, 132, 1)",
              borderWidth: 2,
              tension: 0.4,
            },
          ],
        },
        options: { responsive: true, scales: { y: { beginAtZero: true } } },
      });
    },
  },
};
</script>

<style scoped>
.analytics-container {
  padding: 20px;
  background: #f9fafb;
  border-radius: 12px;
}

.analytics-title {
  font-size: 1.8rem;
  margin-bottom: 25px;
  text-align: center;
  color: #222;
}

/* Summary Cards */
.summary-container {
  display: flex;
  justify-content: center;
  gap: 25px;
  margin-bottom: 30px;
}

.summary-card {
  background: #007bff;
  color: white;
  padding: 20px 30px;
  border-radius: 12px;
  text-align: center;
  box-shadow: 0 3px 10px rgba(0, 0, 0, 0.2);
  min-width: 180px;
}

.summary-card h3 {
  margin: 0;
  font-size: 1.8rem;
}
.summary-card p {
  margin: 8px 0 0;
  font-weight: 500;
  font-size: 1rem;
}

/* Chart containers */
.chart-container {
  background: #fff;
  border-radius: 16px;
  box-shadow: 0 4px 10px rgba(0, 0, 0, 0.1);
  margin-bottom: 25px;
  padding: 20px;
}
</style>
