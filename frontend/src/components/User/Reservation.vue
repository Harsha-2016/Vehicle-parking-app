<template>
  <div>
    <h5>Your Reservations</h5>
    <table class="table table-sm table-striped mt-2">
      <thead>
        <tr>
          <th>Res ID</th>
          <th>Lot</th>
          <th>Spot</th>
          <th>In</th>
          <th>Out</th>
          <th>Cost</th>
          <th>Action</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="r in reservations" :key="r.reservation_id">
          <td>{{ r.reservation_id }}</td>
          <td>{{ r.lot_name }}</td>
          <td>{{ r.spot_id }}</td>
          <td>{{ format(r.parking_timestamp) }}</td>
          <td>{{ r.leaving_timestamp ? format(r.leaving_timestamp) : '-' }}</td>
          <td>{{ r.parking_cost ?? '-' }}</td>
          <td>
            <button class="btn btn-sm btn-warning" v-if="!r.leaving_timestamp" @click="release(r.reservation_id)">
              Release
            </button>
            <span v-else>Done</span>
          </td>
        </tr>
      </tbody>
    </table>
  </div>
</template>

<script>
import API from '@/services/api'
import dayjs from 'dayjs'

export default {
  name: 'ReservationHistory',
  data() {
    return { reservations: [] }
  },
  methods: {
    async loadReservations() {
      try {
        const res = await API.get('/user/me/reservations')
        this.reservations = res.data
      } catch (err) {
        console.error(err)
      }
    },
    format(ts) {
      if (!ts) return '-'
      return dayjs(ts).format('YYYY-MM-DD HH:mm')
    },
    async release(reservation_id) {
      if (!confirm('Release this spot?')) return
      try {
        const res = await API.post('/user/release', { reservation_id })
        alert(`Released. Cost: ${res.data.parking_cost}`)
        this.loadReservations()
        this.$root.$emit('reservations-updated')
      } catch (err) {
        alert(err.response?.data?.error || 'Release failed')
      }
    }
  },
  mounted() {
    this.loadReservations()
    this.$root.$on('reservations-updated', this.loadReservations)
  },
  beforeUnmount() {
    this.$root.$off('reservations-updated', this.loadReservations)
  }
}
</script>
