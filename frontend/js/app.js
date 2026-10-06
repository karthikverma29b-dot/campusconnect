// Shared helpers used by every page.

const TOKEN_KEY = "campusconnect_token";

function getToken() {
  return localStorage.getItem(TOKEN_KEY);
}

function saveToken(token) {
  localStorage.setItem(TOKEN_KEY, token);
}

function logout() {
  localStorage.removeItem(TOKEN_KEY);
  window.location.href = "/index.html";
}

// Call this at the top of any page that needs a logged-in user.
function requireLogin() {
  if (!getToken()) {
    window.location.href = "/index.html";
  }
}

// Wrapper around fetch that adds the login token and handles errors.
async function api(path, options = {}) {
  const headers = { "Content-Type": "application/json" };
  const token = getToken();
  if (token) headers["Authorization"] = "Bearer " + token;

  const response = await fetch("/api" + path, { ...options, headers });
  let data = {};
  try {
    data = await response.json();
  } catch (e) {
    // response had no JSON body
  }

  if (response.status === 401 && token) {
    // token expired or invalid -> back to login
    localStorage.removeItem(TOKEN_KEY);
    window.location.href = "/index.html";
    throw new Error("Please log in again");
  }
  if (!response.ok) {
    throw new Error(formatError(data.detail) || "Something went wrong");
  }
  return data;
}

// FastAPI validation errors come as a list; turn them into one sentence.
function formatError(detail) {
  if (!detail) return "";
  if (typeof detail === "string") return detail;
  if (Array.isArray(detail)) {
    return detail.map((d) => (d.loc ? d.loc[d.loc.length - 1] + ": " : "") + d.msg).join(", ");
  }
  return "Something went wrong";
}

function showMessage(el, text, type = "error") {
  el.textContent = text;
  el.className = "message " + type;
}

function clearMessage(el) {
  el.textContent = "";
  el.className = "message";
}

// Escape text before putting it in innerHTML (prevents HTML injection).
function esc(text) {
  const div = document.createElement("div");
  div.textContent = text == null ? "" : String(text);
  return div.innerHTML;
}

// "In Progress" -> "In-Progress" (used as a CSS class name)
function statusClass(status) {
  return status.replace(/ /g, "-");
}

function statusBadge(status) {
  return `<span class="badge ${statusClass(status)}">${esc(status)}</span>`;
}

// "Lost & Found" -> "lost-found" (used as a CSS class name)
function categoryTag(category) {
  const slug = category.toLowerCase().replace(/[^a-z0-9]+/g, "-").replace(/^-|-$/g, "");
  return `<span class="tag cat-${slug}">${esc(category)}</span>`;
}

// SQLite stores UTC like "2026-10-05 08:30:00".
function formatDate(value) {
  const d = new Date(value.replace(" ", "T") + "Z");
  return d.toLocaleString(undefined, { dateStyle: "medium", timeStyle: "short" });
}

// Draw the top navigation bar on logged-in pages.
function renderNavbar(active) {
  const links = [
    ["dashboard.html", "Dashboard"],
    ["create.html", "New issue"],
    ["profile.html", "Profile"],
  ];
  const items = links
    .map(([href, label]) => `<a href="/${href}" class="${active === href ? "active" : ""}">${label}</a>`)
    .join("");
  document.getElementById("navbar").innerHTML = `
    <a class="brand" href="/dashboard.html"><span class="brand-mark">!</span>CampusConnect</a>
    <nav>${items}<a href="#" id="logout-link">Log out</a></nav>`;
  document.getElementById("logout-link").addEventListener("click", (e) => {
    e.preventDefault();
    logout();
  });
}
