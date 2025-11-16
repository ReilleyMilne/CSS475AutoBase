import { escapeHtml, formatLabel } from "../shared.js";

// =========================
// Page Initialization
// =========================
document.addEventListener("DOMContentLoaded", async () => {
  await new Promise(resolve => setTimeout(resolve, 100));
  await loadCustomerInfo();
});

// =========================
// Load Customer Info
// =========================
async function loadCustomerInfo() {
  try {
    const response = await fetch(`${BACKEND_URL}/api/customer/info`, {
      method: "GET",
      credentials: "include"
    });

    const data = await response.json();
    if (!response.ok) {
      console.error("Failed to load customer info:", data.error);
      return;
    }

    renderCustomerInfo(data.customer);

  } catch (err) {
    console.error("Error loading customer info:", err);
  }
}

// =========================
// Render Customer Details
// =========================
function renderCustomerInfo(customer) {
  const container = document.getElementById("customerInfo");
  const loading = document.getElementById("customerInfoLoading");
  const error = document.getElementById("customerInfoError");

  if (!container) return;

  // Hide loading spinner
  if (loading) loading.style.display = "none";

  // Hide error message
  if (error) error.style.display = "none";

  // Build the table HTML
  let html = `
    <table class="customer-details-table">
      <tbody>
  `;

  for (const [key, value] of Object.entries(customer)) {
    html += `
      <tr>
        <td class="label">${formatLabel(key)}</td>
        <td class="value">${escapeHtml(value ?? "")}</td>
      </tr>
    `;
  }

  html += `
      </tbody>
    </table>
  `;

  container.innerHTML = html;
}
