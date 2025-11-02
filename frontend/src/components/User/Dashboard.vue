<template>
  <div class="container mt-4">
    <h3>User Dashboard</h3>

    <h5 class="mt-3">Available Parking Lots</h5>
    <table class="table table-bordered mt-2">
      <thead>
        <tr>
          <th>Lot ID</th>
          <th>Location</th>
          <th>Price/hr</th>
          <th>Total</th>
          <th>Available</th>
          <th>Action</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="lot in lots" :key="lot.lot_id">
          <td>{{ lot.lot_id }}</td>
          <td>{{ lot.prime_location_name }}</td>
          <td>{{ lot.price }}</td>
          <td>{{ lot.total_spots }}</td>
          <td>{{ lot.available_spots }}</td>
          <td>
            <button class="btn btn-sm btn-primary" :disabled="lot.available_spots === 0" @click="reserve(lot.lot_id)">
              Reserve
            </button>
          </td>
        </tr>
      </tbody>
    </table>

    <hr />

    <reservation-history />
  </div>
</template>

<script>
import API from '@/services/api'
import ReservationHistory from './Reservation.vue'

export default {
  components: { ReservationHistory },
  data() {
    return {
      lots: []
    }
  },
  methods: {
    async loadLots() {
      try {
        const res = await API.get('/user/lots')
        this.lots = res.data
      } catch (err) {
        console.error(err)
        alert(err.response?.data?.error || 'Failed to load lots')
      }
    },
    async reserve(lotId) {
      try {
        const res = await API.post('/user/reserve', { lot_id: lotId })
        alert('Reserved! Spot ID: ' + res.data.spot_id)
        this.loadLots()
        // Also tell the history component to refresh (emit event or use a simple solution)
        this.$root.$emit('reservations-updated')
      } catch (err) {
        console.error(err)
        alert(err.response?.data?.error || 'Reserve failed')
      }
    }
  },
  mounted() {
    this.loadLots()
    // refresh after reservations changed
    this.$root.$on('reservations-updated', this.loadLots)
  },
  beforeUnmount() {
    this.$root.$off('reservations-updated', this.loadLots)
  }
}
</script>
