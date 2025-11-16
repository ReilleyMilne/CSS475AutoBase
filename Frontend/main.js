// =========================
// Configuration
// =========================
const BACKEND_URL = "http://127.0.0.1:5000";

document.addEventListener("DOMContentLoaded", async () => {
  const navbarContainer = document.getElementById("navbar");
  if (navbarContainer) await loadNavbar(navbarContainer);

  const loginForm = document.getElementById("loginForm");

  // Try to fetch the currently logged-in user
  const user = await safeFetchCurrentUser();
  console.log("Current user:", user); // Debug log
  
  handlePageProtection(user);
  updateNavbarState(user);

  // Handle login form submission
  if (loginForm) {
    loginForm.addEventListener("submit", async (e) => {
      e.preventDefault();
      await handleLogin();
    });
  }
});

// =========================
// Navbar Loader
// =========================
async function loadNavbar(container) {
  try {
    const response = await fetch("/Frontend/navbar.html");
    if (!response.ok) throw new Error(`Failed to load navbar: ${response.status}`);
    container.innerHTML = await response.text();

    const loginBtn = document.getElementById("loginBtn");
    const logoutBtn = document.getElementById("logoutBtn");

    if (loginBtn) loginBtn.addEventListener("click", () => (window.location.href = "/Frontend/login.html"));
    if (logoutBtn) logoutBtn.addEventListener("click", handleLogout);
  } catch (err) {
    logError("loadNavbar", err);
  }
}

// =========================
// Login
// =========================
async function handleLogin() {
  const username = document.getElementById("username").value.trim();
  const password = document.getElementById("password").value.trim();
  const role = document.getElementById("role").value;

  if (!role) {
    alert("Please select a role before logging in.");
    return;
  }

  try {
    const response = await fetch(`${BACKEND_URL}/api/auth/login`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ username, password, user_type: role }),
      credentials: "include"
    });

    const data = await response.json().catch(() => ({}));
    
    if (!response.ok) {
      const reason = data.error || `HTTP ${response.status}`;
      throw new Error(`Login failed: ${reason}`);
    }

    // Session is stored server-side, no need for localStorage
    alert(`Logged in successfully as ${role}: ${username}`);

    // Redirect based on role
    if (role === "employee") {
      window.location.href = "/Frontend/employee/employee.html";
    } else {
      window.location.href = "/Frontend/customer/customer.html";
    }
  } catch (err) {
    logError("handleLogin", err);
    alert("Login failed. Please check your credentials or try again later.");
  }
}

// =========================
// Logout
// =========================
async function handleLogout() {
  try {
    const response = await fetch(`${BACKEND_URL}/api/auth/logout`, {
      method: "POST",
      credentials: "include"
    });

    if (!response.ok) throw new Error(`Logout failed: HTTP ${response.status}`);

    alert("Logged out successfully!");
    window.location.href = "/Frontend/index.html";
  } catch (err) {
    logError("handleLogout", err);
    alert("An issue occurred while logging out. You may need to clear your cookies manually.");
  }
}

// =========================
// Current User
// =========================
async function safeFetchCurrentUser() {
  try {
    const response = await fetch(`${BACKEND_URL}/api/auth/current_user`, {
      method: "GET",
      credentials: "include"
    });

    if (!response.ok) {
      throw new Error(`Failed to fetch current user: HTTP ${response.status}`);
    }

    const data = await response.json();
    
    // Handle both formats: {user: {...}} or {...}
    // Return null if user is explicitly null or undefined
    if (data.user !== undefined) {
      return data.user; // Backend wraps in {user: ...}
    }
    
    // If data has username property, it's the user object itself
    if (data.username) {
      return data;
    }
    
    return null;
  } catch (err) {
    logError("safeFetchCurrentUser", err);
    return null;
  }
}

// =========================
// Navbar State Update
// =========================
function updateNavbarState(user) {
  const loginBtn = document.getElementById("loginBtn");
  const logoutBtn = document.getElementById("logoutBtn");
  const userGreeting = document.getElementById("userGreeting");
  const navLeft = document.querySelector(".nav-left");

  if (!navLeft) return;

  // Always show home link
  navLeft.innerHTML = `
    <a href="/Frontend/index.html" class="logo">AutoBase</a>
    <a href="/Frontend/index.html">Home</a>
  `;

  if (user && user.username) {
    // User is logged in
    if (loginBtn) loginBtn.style.display = "none";
    if (logoutBtn) logoutBtn.style.display = "inline-block";
    if (userGreeting) userGreeting.textContent = `👋 ${user.username} (${user.user_type})`;

    // Add role-specific nav links
    if (user.user_type === "employee") {
      navLeft.innerHTML += `
        <a href="/Frontend/employee/employee.html">Dashboard</a>
        <a href="#">Reports</a>
      `;
    } else if (user.user_type === "customer") {
      navLeft.innerHTML += `
        <a href="/Frontend/customer/customer.html">My Account</a>
        <a href="/Frontend/vehicles/vehicles.html">Vehicles</a>
      `;
    }
  } else {
    // User is not logged in
    if (loginBtn) loginBtn.style.display = "inline-block";
    if (logoutBtn) logoutBtn.style.display = "none";
    if (userGreeting) userGreeting.textContent = "";
  }
}

// =========================
// Page Protection
// =========================
function handlePageProtection(user) {
  const path = window.location.pathname.split("/").pop();

  // Protect employee page
  if (path === "/Frontend/employee/employee.html" && (!user || user.user_type !== "employee")) {
    alert("Unauthorized access. Employee accounts only.");
    window.location.href = "/Frontend/login.html";
    return;
  }
  
  // Protect customer page
  if (path === "/Frontend/customer/customer.html" && (!user || user.user_type !== "customer")) {
    alert("Unauthorized access. Customer accounts only.");
    window.location.href = "/Frontend/login.html";
    return;
  }
}

// =========================
// Centralized Error Logger
// =========================
function logError(context, error) {
  console.group(`Error in ${context}`); // Fixed: was using single quotes instead of backticks
  console.error("Message:", error.message || error);
  if (error.stack) console.error("Stack:", error.stack);
  console.groupEnd();
}