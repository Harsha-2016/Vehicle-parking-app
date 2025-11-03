<template>
  <div class="lots-container">
    <h2>Create New Parking Lot</h2>

    <form @submit.prevent="createLot" class="lot-form">
      <div class="form-group">
        <label>Prime Location Name</label>
        <input
          v-model="newLot.prime_location_name"
          type="text"
          placeholder="Enter location name"
          required
        />
      </div>

      <div class="form-group">
        <label>Price per Hour (₹)</label>
        <input
          v-model.number="newLot.price_per_hour"
          type="number"
          step="0.01"
          placeholder="Enter price"
          required
        />
      </div>

      <div class="form-group">
        <label>Address</label>
        <input
          v-model="newLot.address"
          type="text"
          placeholder="Enter address"
        />
      </div>

      <div class="form-group">
        <label>Pin Code</label>
        <input
          v-model="newLot.pin_code"
          type="text"
          placeholder="Enter pin code"
        />
      </div>

      <div class="form-group">
        <label>Number of Spots</label>
        <input
          v-model.number="newLot.number_of_spots"
          type="number"
          placeholder="Enter number of spots"
          required
        />
      </div>

      <button type="submit" class="btn-submit">
        Create Parking Lot
      </button>
    </form>

    <hr />

    <h3>Existing Parking Lots</h3>
    <table class="lot-table" v-if="lots.length">
      <thead>
        <tr>
          <th>ID</th>
          <th>Location</th>
          <th>Price/hr (₹)</th>
          <th>Available spots</th>
          <th>Occupied spots</th>
          <th>Address</th>
          <th>Pin</th>
          <th>Actions</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="lot in lots" :key="lot.id">
          <td>{{ lot.id }}</td>
          <td>{{ lot.prime_location_name }}</td>
          <td>{{ lot.price_per_hour }}</td>
          <td>{{ lot.available_spots }}</td>
          <td>{{ lot.occupied_spots }}</td>
          <td>{{ lot.address }}</td>
          <td>{{ lot.pin_code }}</td>
          <td>
            <button class="btn-view" @click="viewSpots(lot.id)">View</button>
            <button class="btn-edit" @click="editLot(lot)">Edit</button>
            <button class="btn-delete" @click="deleteLot(lot.id)">Delete</button>
          </td>
        </tr>
      </tbody>
    </table>

    <p v-else class="no-lots">No parking lots available yet.</p>
    <!-- Edit Lot Modal -->
    <div v-if="editingLot" class="modal-overlay">
      <div class="modal-content">
        <h3>Edit Parking Lot</h3>
        <form @submit.prevent="updateLot">
          <label>Prime Location Name</label>
          <input v-model="editingLot.prime_location_name" required />

          <label>Price per Hour (₹)</label>
          <input v-model.number="editingLot.price_per_hour" type="number" step="0.01" required />
        

          <label>Address</label>
          <input v-model="editingLot.address" />

          <label>Pin Code</label>
          <input v-model="editingLot.pin_code" />

          <label>Number of Spots</label>
          <input v-model.number="editingLot.number_of_spots" type="number" step="0.01" required />

          <div class="modal-buttons">
            <button type="submit" class="save-btn">Save</button>
            <button type="button" class="cancel-btn" @click="cancelEdit">Cancel</button>
          </div>
        </form>
      </div>
    </div>

    <!-- View Spots Modal -->
    <div v-if="selectedSpots" class="modal-overlay">
      <div class="modal-content">
        <h3>Spots for Lot ID: {{ selectedLotId }}</h3>
        <ul v-if="selectedSpots.length">
          <li v-for="spot in selectedSpots" :key="spot.spot_id">
            Spot ID: {{ spot.spot_id }} — Status: {{ spot.status }}
          </li>
        </ul>
        <p v-else>No spots found.</p>
        <button class="cancel-btn" @click="closeSpots">Close</button>
      </div>
    </div>
  </div>
</template>

<script>
import axios from "axios";

export default {
  name: "Lots",
  data() {
    return {
      newLot: {
        prime_location_name: "",
        price_per_hour: null,
        address: "",
        pin_code: "",
        number_of_spots: null,
      },
      lots: [],
      editingLot: null,
      selectedSpots: null,
      selectedLotId: null,
    };
  },
  async mounted() {
    this.fetchLots();
  },
  methods: {
    async fetchLots() {
      try {
        const token = localStorage.getItem("token");
        const response = await axios.get("http://127.0.0.1:5000/admin/lots", {
          headers: { Authorization: `Bearer ${token}` },
        });
        this.lots = response.data;
        console.log("Fetched lots:", this.lots);
      } catch (err) {
        console.error("Error fetching lots:", err.message);
      }
    },

    async createLot() {
      try {
        const token = localStorage.getItem("token");
        const lotData = { ...this.newLot };

        const response = await axios.post(
          "http://127.0.0.1:5000/admin/create_lot",
          lotData,
          {
            headers: {
              "Content-Type": "application/json",
              Authorization: `Bearer ${token}`,
            },
          }
        );

        alert(response.data.message || "Parking lot created successfully!");
        console.log("Create response:", response);
        this.fetchLots(); // refresh list
        this.newLot = {
          prime_location_name: "",
          price_per_hour: null,
          address: "",
          pin_code: "",
          number_of_spots: null,
        };
      } catch (err) {
        console.error("Error creating lot:", err.response?.data || err.message);
      }
    },
    editLot(lot) {
      if (lot.occupied_spots > 0) {
        alert("⚠️ Cannot edit this lot while spots are occupied.");
      return;
     }
      this.editingLot = { ...lot }; // create a copy for editing
      console.log("Editing lot:", this.editingLot);
    },

    async updateLot() {
      try {
        const token = localStorage.getItem("token");
        const response = await axios.put(
          `http://127.0.0.1:5000/admin/update_lot/${this.editingLot.id}`,
          this.editingLot,
          { headers: { Authorization: `Bearer ${token}` } }
        );
        alert(response.data.message || "Lot updated successfully!");
        console.log("Update response:", response);
        this.editingLot = null;
        this.fetchLots();
      } catch (err) {
        console.error("Error updating lot:", err.response?.data || err.message);
      }
    },

    async deleteLot(id) {
      const lot = this.lots.find(l => l.id === id);
      if (lot && lot.occupied_spots > 0) {
        alert("⚠️ Cannot delete this lot while spots are occupied.");
      return;
      }

      if (!confirm("Are you sure you want to delete this parking lot?")) return;
      
      try {
        const token = localStorage.getItem("token");
        const response = await axios.delete(
          `http://127.0.0.1:5000/admin/delete_lot/${id}`,
          { headers: { Authorization: `Bearer ${token}` } }
        );
        alert(response.data.message || "Parking lot deleted successfully!");
        this.fetchLots();
      } catch (err) {
        console.error("Error deleting lot:", err.response?.data || err.message);
      }
    },

    async viewSpots(id) {
      this.$router.push({ name: "LotSpots", params: { lot_id: id } });
    },

    cancelEdit() {
      this.editingLot = null;
    },

    closeSpots() {
      this.selectedSpots = null;
    },

  },
};
</script>
<style scoped>
.lots-container {
  max-width: 900px;
  margin: auto;
  padding: 20px;
}

.lot-form {
  background-color: #f9f9fb;
  padding: 20px;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  margin-bottom: 30px;
}

.form-group {
  margin-bottom: 15px;
}

label {
  font-weight: 600;
  display: block;
  margin-bottom: 5px;
}

input {
  width: 100%;
  padding: 8px 10px;
  border-radius: 6px;
  border: 1px solid #ccc;
}

.btn-submit {
  background-color: #007bff;
  color: white;
  padding: 10px 14px;
  border-radius: 6px;
  border: none;
  cursor: pointer;
  font-weight: 600;
}
.btn-submit:hover {
  background-color: #0056b3;
}

.lot-table {
  width: 100%;
  border-collapse: collapse;
  margin-top: 20px;
}

.lot-table th,
.lot-table td {
  border: 1px solid #ddd;
  padding: 10px;
  text-align: center;
}

.lot-table th {
  background-color: #007bff;
  color: white;
}

.btn-view,
.btn-edit,
.btn-delete {
  border: none;
  padding: 6px 10px;
  border-radius: 5px;
  cursor: pointer;
  color: white;
  font-weight: 500;
  margin-right: 5px;
}

.btn-view { background-color: #28a745; }
.btn-edit { background-color: #ffc107; color: #333; }
.btn-delete { background-color: #dc3545; }

.btn-view:hover { background-color: #218838; }
.btn-edit:hover { background-color: #e0a800; }
.btn-delete:hover { background-color: #c82333; }

.modal-overlay {
  position: fixed;
  top: 0; left: 0;
  width: 100%; height: 100%;
  background: rgba(0,0,0,0.4);
  display: flex;
  justify-content: center;
  align-items: center;
}

.modal-content {
  background: white;
  padding: 20px;
  border-radius: 10px;
  width: 400px;
}

.modal-buttons {
  margin-top: 15px;
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}

.save-btn { background: #007bff; color: white; border: none; padding: 8px 12px; border-radius: 6px; }
.cancel-btn { background: #6c757d; color: white; border: none; padding: 8px 12px; border-radius: 6px; }
</style>