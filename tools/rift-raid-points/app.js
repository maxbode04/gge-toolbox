/* Rift Raid Points calculator */
(function () {
  "use strict";

  let BOSSES = [];
  const $ = (id) => document.getElementById(id);
  const num = (n) => Math.round(n).toLocaleString();

  function curLevel() {
    const boss = BOSSES[+$("boss").value] || BOSSES[0];
    return boss.levels[+$("level").value] || boss.levels[0];
  }

  function fillLevels() {
    const boss = BOSSES[+$("boss").value] || BOSSES[0];
    $("level").innerHTML = boss.levels.map((l, i) =>
      '<option value="' + i + '">Level ' + l.level + "</option>").join("");
  }

  function renderMult() {
    const l = curLevel();
    $("mult").innerHTML =
      cell("×" + num(l.wallPointFactor), "Wall multiplier (full segment)") +
      cell("×" + num(l.courtyardPointFactor), "Courtyard multiplier (full clear)") +
      cell(num(l.minPointsForRewards), "Eligibility threshold");
  }
  function cell(v, k) {
    return '<div class="cell"><div class="v">' + v + '</div><div class="k">' + k + "</div></div>";
  }

  function recompute() {
    const l = curLevel();
    const cyClears = Math.max(0, +$("cyClears").value || 0);
    const cyPct = Math.max(0, Math.min(100, +$("cyPct").value || 0)) / 100;
    const wallClears = Math.max(0, +$("wallClears").value || 0);
    const wallPct = Math.max(0, Math.min(100, +$("wallPct").value || 0)) / 100;

    const cyPoints = cyClears * cyPct * l.courtyardPointFactor;
    const wallPoints = wallClears * wallPct * l.wallPointFactor;
    const total = cyPoints + wallPoints;
    const threshold = l.minPointsForRewards;
    const pct = threshold > 0 ? Math.min(1, total / threshold) : 1;
    const qualified = total >= threshold;

    // How many more full courtyard clears to qualify?
    let need = "";
    if (!qualified && l.courtyardPointFactor > 0) {
      const remaining = threshold - total;
      const moreCy = Math.ceil(remaining / l.courtyardPointFactor);
      need = " — about <b>" + moreCy + "</b> more full courtyard clear" + (moreCy === 1 ? "" : "s") + " to qualify.";
    }

    $("results").innerHTML =
      '<div class="rp-total"><span class="big">' + num(total) + '</span><span class="lbl">activity points</span></div>' +
      '<div class="rp-bar-wrap">' +
        '<div class="rp-bar-meta"><span>Boss Defeat eligibility</span><span>' + num(total) + " / " + num(threshold) + "</span></div>" +
        '<div class="rp-bar"><div class="rp-bar-fill ' + (qualified ? "ok" : "") + '" style="width:' + (pct * 100).toFixed(1) + '%"></div></div>' +
      "</div>" +
      '<div class="rp-verdict ' + (qualified ? "ok" : "no") + '">' +
        (qualified ? "✅ <b>Eligible</b> for the Boss Defeat reward." : "Not yet eligible" + need) +
      "</div>" +
      '<div class="rp-breakdown">' +
        row("Courtyard (" + cyClears + " × " + Math.round(cyPct * 100) + "% × ×" + num(l.courtyardPointFactor) + ")", num(cyPoints)) +
        row("Wall (" + wallClears + " × " + Math.round(wallPct * 100) + "% × ×" + num(l.wallPointFactor) + ")", num(wallPoints)) +
      "</div>";
  }
  function row(k, v) {
    return '<div class="row"><span>' + k + "</span><b>" + v + "</b></div>";
  }

  function refresh() { renderMult(); recompute(); }

  fetch("../overview-rift/data/rift-bosses.json")
    .then((r) => r.json())
    .then((d) => {
      BOSSES = d.bosses;
      $("boss").innerHTML = BOSSES.map((b, i) =>
        '<option value="' + i + '">' + b.name + "</option>").join("");
      fillLevels();
      $("boss").addEventListener("change", () => { fillLevels(); refresh(); });
      $("level").addEventListener("change", refresh);
      ["cyClears", "cyPct", "wallClears", "wallPct"].forEach((id) =>
        $(id).addEventListener("input", recompute));
      refresh();
    })
    .catch((e) => {
      $("results").innerHTML = '<p class="muted">Could not load rift data.</p>';
      console.error(e);
    });
})();
