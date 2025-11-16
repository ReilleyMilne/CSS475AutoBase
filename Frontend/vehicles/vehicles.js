import {
  escapeHtml,
  formatMileage,
  showLoading,
  hideLoading
} from "/Frontend/shared.js";

// =========================
// Page Initialization
// =========================
document.addEventListener("DOMContentLoaded", async () => {
  await new Promise(resolve => setTimeout(resolve, 100));
  await loadCustomerVehicles();
  setupEventListeners();
});

// =========================
// Load Customer Vehicles
// =========================
async function loadCustomerVehicles() {
  const loadingMessage = document.getElementById("loadingMessage");
  const errorMessage = document.getElementById("errorMessage");
  const vehiclesContainer = document.getElementById("vehiclesContainer");

  showLoading(loadingMessage);
  if (errorMessage) errorMessage.style.display = "none";
  if (vehiclesContainer) vehiclesContainer.innerHTML = "";

  try {
    const response = await fetch(`${BACKEND_URL}/api/customer/vehicles`, {
      method: "GET",
      credentials: "include"
    });

    const data = await response.json();
    if (!response.ok) throw new Error(data.error);

    hideLoading(loadingMessage);

    const vehicles = data.vehicles || [];

    if (vehicles.length === 0) {
      displayNoVehicles(vehiclesContainer);
    } else {
      displayVehicles(vehicles, vehiclesContainer);
    }

  } catch (error) {
    console.error("Error loading vehicles:", error);

    hideLoading(loadingMessage);

    if (errorMessage) {
      errorMessage.textContent =
        `Failed to load vehicles: ${error.message}`;
      errorMessage.style.display = "block";
    }
  }
}

// =========================
// Event Listeners
// =========================
function setupEventListeners() {
  const refreshBtn = document.getElementById("refreshBtn");
  if (refreshBtn) {
    refreshBtn.addEventListener("click", async () => {
      refreshBtn.disabled = true;
      refreshBtn.innerHTML = "⏳ Refreshing...";
      await loadCustomerVehicles();
      refreshBtn.disabled = false;
      refreshBtn.innerHTML = "🔄 Refresh";
    });
  }
}

// =========================
// Display Vehicle Cards
// =========================
function displayNoVehicles(container) {
  container.innerHTML = `
    <div class="no-vehicles">
      <h3>No Vehicles Found</h3>
      <p>You currently don't have any vehicles.</p>
    </div>
  `;
}

function displayVehicles(vehicles, container) {
  container.innerHTML = vehicles.map(createVehicleCard).join("");
}

function createVehicleCard(vehicle) {
  return `
    <div class="vehicle-card">
      <div class="vehicle-header">
        <h3>${escapeHtml(vehicle.Make)} ${escapeHtml(vehicle.Model)}</h3>
        <p class="vehicle-year">${vehicle.Year}</p>
      </div>

      <div class="vehicle-details">
        <p><strong>VIN:</strong> ${escapeHtml(vehicle.VIN)}</p>
        <p><strong>Color:</strong> ${escapeHtml(vehicle.Color)}</p>
        <p><strong>Mileage:</strong> ${formatMileage(vehicle.Mileage)}</p>
      </div>
    </div>
  `;
}
