const $ = (sel) => document.querySelector(sel);
const form = $("#search-form");
const input = $("#user-input");
const errorEl = $("#form-error");
const results = $("#results");
const grid = $("#rec-grid");
const historyList = $("#history-list");
const chips = $("#chips");

const esc = (s) => String(s).replace(/[&<>"']/g, (c) =>
  ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));

async function getJSON(url) {
  const res = await fetch(url);
  const data = await res.json();
  if (!res.ok) throw new Error(data.error || "Something went wrong.");
  return data;
}

function skeletons(n) {
  return Array.from({ length: n }, () => '<div class="card skeleton"></div>').join("");
}

function movieCard(m, i) {
  const hue = (m.movie_id * 47) % 360;
  const badge = m.title.startsWith("Movie #") ? "🎞" : esc(m.title.charAt(0));
  return `
    <article class="card movie" style="--h:${hue}deg; animation-delay:${i * 60}ms">
      <div class="poster"><span>${badge}</span></div>
      <div class="info">
        <div class="rank">#${i + 1}</div>
        <h3 title="${esc(m.title)}">${esc(m.title)}</h3>
        <p class="genres">${esc(m.genres || "Genres pending")}</p>
        <div class="predict">
          <span class="stars-big">★ ${m.predicted.toFixed(2)}</span>
          <span class="match-label">${m.match}% match</span>
        </div>
        <div class="match-bar"><div class="match-fill" data-w="${m.match}"></div></div>
      </div>
    </article>`;
}

async function showViewer(userId) {
  errorEl.hidden = true;
  results.hidden = false;
  $("#viewer-title").textContent = `Viewer ${userId}`;
  $("#viewer-meta").textContent = "Finding recommendations…";
  historyList.innerHTML = "";
  grid.innerHTML = skeletons(6);
  results.scrollIntoView({ behavior: "smooth", block: "start" });

  try {
    const d = await getJSON(`/api/recommend?user=${userId}&n=12`);
    $("#viewer-meta").textContent = `Has rated ${d.rated_count} movies in our sample`;

    historyList.innerHTML = d.history.map((m) =>
      `<div class="history-item"><span class="stars">${"★".repeat(m.rating)}</span>${esc(m.title)}</div>`
    ).join("");

    grid.innerHTML = d.recommendations.map(movieCard).join("");

    requestAnimationFrame(() =>
      document.querySelectorAll(".match-fill").forEach((el) => {
        el.style.width = el.dataset.w + "%";
      })
    );

    const url = new URL(location.href);
    url.searchParams.set("user", userId);
    window.history.replaceState(null, "", url);
  } catch (err) {
    results.hidden = true;
    errorEl.textContent = err.message;
    errorEl.hidden = false;
  }
}

form.addEventListener("submit", (e) => {
  e.preventDefault();
  const id = parseInt(input.value, 10);
  if (!Number.isInteger(id) || id < 1) {
    errorEl.textContent = "Please enter a valid numeric viewer ID.";
    errorEl.hidden = false;
    return;
  }
  showViewer(id);
});

$("#random-btn").addEventListener("click", async () => {
  const { users } = await getJSON("/api/random?count=1");
  input.value = users[0];
  showViewer(users[0]);
});

chips.addEventListener("click", (e) => {
  const id = e.target.dataset.id;
  if (id) {
    input.value = id;
    showViewer(id);
  }
});

function animateNumber(sel, target) {
  const el = $(sel);
  const start = performance.now();
  const duration = 1200;
  const tick = (now) => {
    const p = Math.min((now - start) / duration, 1);
    el.textContent = Math.round(target * (1 - Math.pow(1 - p, 3))).toLocaleString();
    if (p < 1) requestAnimationFrame(tick);
  };
  requestAnimationFrame(tick);
}

async function init() {
  try {
    const s = await getJSON("/api/stats");
    animateNumber("#stat-users", s.users);
    animateNumber("#stat-movies", s.movies);
    animateNumber("#stat-ratings", s.ratings);
    $("#stat-rmse").textContent = s.metrics.svd.rmse.toFixed(3);

    const { users } = await getJSON("/api/random?count=5");
    chips.innerHTML = '<span class="muted-label">Try:</span>' +
      users.map((id) => `<button class="chip" data-id="${id}">${id}</button>`).join("");
  } catch (err) {
    console.error(err);
  }

  const preset = new URLSearchParams(location.search).get("user");
  if (preset) {
    input.value = preset;
    showViewer(preset);
  }
}

init();