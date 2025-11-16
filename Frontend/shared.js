// =========================
// Shared Helper Functions
// =========================
export function escapeHtml(text) {
  if (!text) return "";
  const map = {
    "&": "&amp;",
    "<": "&lt;",
    ">": "&gt;",
    '"': "&quot;",
    "'": "&#039;"
  };
  return String(text).replace(/[&<>"']/g, m => map[m]);
}

export function formatMileage(mileage) {
  if (!mileage && mileage !== 0) return "N/A";
  return new Intl.NumberFormat("en-US").format(mileage) + " miles";
}

export function formatLabel(field) {
  return field
    .replace(/_/g, " ")
    .replace(/([A-Z])/g, " $1")
    .replace(/\b\w/g, (c) => c.toUpperCase())
    .trim();
}

export function showLoading(element) {
  if (element) {
    element.style.display = "block";
  }
}

export function hideLoading(element) {
  if (element) {
    element.style.display = "none";
  }
}
