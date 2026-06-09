/* Maxy's Empire Toolkit — homepage feed renderer.
   Renders the What's New changelog, GGS news and the events plan from
   assets/data/site-feed.json so they can be kept current (by hand or by the
   data-refresh GitHub Action) without touching index.html. */
(function () {
  "use strict";

  function esc(s) {
    return String(s == null ? "" : s).replace(/[&<>"]/g, (c) =>
      ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]));
  }

  function renderChangelog(list) {
    const el = document.getElementById("changelog");
    if (!el || !list) return;
    el.innerHTML = list.map((c) =>
      `<li>
        <span class="cl-date">${esc(c.date)}</span>
        <span class="cl-body"><b>${esc(c.title)}</b> — ${esc(c.body)}</span>
      </li>`).join("");
  }

  function renderNews(list, allUrl) {
    const el = document.getElementById("news-list");
    if (!el || !list) return;
    el.innerHTML = list.map((n) =>
      `<li class="news-item">
        <span class="news-date">${esc(n.date)}</span>
        <a class="news-title" href="${esc(n.url)}" target="_blank" rel="noopener">${esc(n.title)}</a>
      </li>`).join("");
    const all = document.getElementById("news-all");
    if (all && allUrl) all.href = allUrl;
  }

  function renderEvents(events) {
    const head = document.getElementById("events-head");
    const grid = document.getElementById("events-grid");
    if (!grid || !events) return;
    if (head && events.month) head.textContent = "📅 Upcoming Events — " + events.month;
    const base = events.iconBase || "";
    grid.innerHTML = (events.items || []).map((ev) => {
      const icon = ev.icon
        ? `<img class="ev-ico" src="${esc(base + ev.icon)}" alt="" loading="lazy"
             onerror="this.outerHTML='<span class=&quot;ev-emoji&quot;>${esc(ev.emoji || "•")}</span>'">`
        : `<span class="ev-emoji">${esc(ev.emoji || "•")}</span>`;
      return `<div class="event-chip">
        <div class="event-chip-name">${icon}${esc(ev.name)}</div>
        <div class="event-chip-dates">${esc(ev.dates)}</div>
      </div>`;
    }).join("");
  }

  fetch("assets/data/site-feed.json?v=" + Date.now())
    .then((r) => r.json())
    .then((d) => {
      renderChangelog(d.changelog);
      renderNews(d.news, d.newsUrl);
      renderEvents(d.events);
    })
    .catch((e) => console.error("home-feed:", e));
})();
