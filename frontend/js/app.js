/* Verifai — Minimalist Frontend Logic */

const API = "";
let scoreChart = null;

const EXAMPLES = {
  real:  "Scientists at MIT published research showing that a new solar panel material achieves 40% efficiency, according to a study released in the journal Nature Energy. Researchers say the findings could significantly reduce the cost of renewable energy production worldwide.",
  fake:  "SHOCKING!!! Scientists EXPOSED covering up MIRACLE cure that DESTROYS cancer overnight!!! They DON'T want you to know this secret! Share before they DELETE this! You WON'T BELIEVE what they found — the government has been hiding this for decades!!!",
  mixed: "Local authorities confirmed an unusual incident near the town hall yesterday. Several witnesses reported seeing strange lights in the sky, though officials have not yet released an official explanation for what occurred in the area.",
};

// ── Word counter ──────────────────────────────────────────────────────────────
document.getElementById("textInput").addEventListener("input", function () {
  const w = this.value.trim() ? this.value.trim().split(/\s+/).length : 0;
  document.getElementById("wordCount").textContent = `${w} word${w !== 1 ? "s" : ""}`;
});

function loadEx(key) {
  document.getElementById("textInput").value = EXAMPLES[key];
  document.getElementById("textInput").dispatchEvent(new Event("input"));
}

function clearAll() {
  document.getElementById("textInput").value = "";
  document.getElementById("wordCount").textContent = "0 words";
}

// ── Status helpers ────────────────────────────────────────────────────────────
function setStatus(state, text) {
  document.getElementById("statusDot").className   = `status-dot ${state}`;
  document.getElementById("statusLabel").textContent = text;
}

// ── Analyse ───────────────────────────────────────────────────────────────────
async function analyse() {
  const text = document.getElementById("textInput").value.trim();
  if (!text) return;

  const btn = document.getElementById("analyseBtn");
  document.getElementById("btnText").classList.add("hidden");
  document.getElementById("btnSpinner").classList.remove("hidden");
  btn.disabled = true;
  setStatus("loading", "Analysing…");

  try {
    const res  = await fetch(API + "/api/analyze", {
      method:  "POST",
      headers: { "Content-Type": "application/json" },
      body:    JSON.stringify({ text }),
    });
    const data = await res.json();
    if (data.error) { alert(data.error); return; }
    render(data);
    setStatus("ready", "Complete");
  } catch {
    alert("Cannot connect to server. Make sure Flask is running on port 5001.");
    setStatus("error", "Offline");
  } finally {
    document.getElementById("btnText").classList.remove("hidden");
    document.getElementById("btnSpinner").classList.add("hidden");
    btn.disabled = false;
  }
}

// ── Render results ────────────────────────────────────────────────────────────
function render(d) {
  document.getElementById("emptyState").classList.add("hidden");
  document.getElementById("results").classList.remove("hidden");

  // Verdict banner
  const banner = document.getElementById("verdictBanner");
  const isCredible = d.verdict.includes("Credible");
  const isUncertain = d.verdict.includes("Uncertain");
  const cls = isCredible ? "credible" : isUncertain ? "uncertain" : "fake";
  banner.className = `verdict-banner ${cls}`;

  const icons = { credible: "✓", uncertain: "~", fake: "✕" };
  document.getElementById("verdictIcon").textContent  = icons[cls];
  document.getElementById("verdictTitle").textContent = d.verdict;
  document.getElementById("verdictSub").textContent   = `Credibility score: ${d.score_pct}%`;
  document.getElementById("verdictScore").textContent = `${d.score_pct}%`;

  // Score bar marker (0–100% position)
  document.getElementById("scoreMarker").style.left = `${d.score_pct}%`;

  // Stats
  document.getElementById("statCB").textContent = d.clickbait_patterns;
  document.getElementById("statCM").textContent = d.credible_markers;
  document.getElementById("statSW").textContent = d.sensational_words.length;
  document.getElementById("statWC").textContent = d.word_count;

  // Score breakdown chart
  if (scoreChart) { scoreChart.destroy(); scoreChart = null; }
  const ctx = document.getElementById("scoreChart").getContext("2d");
  scoreChart = new Chart(ctx, {
    type: "bar",
    data: {
      labels: ["ML Score", "Pattern Score", "Final Score"],
      datasets: [{
        data: [d.features.ml_score, d.features.pattern_score, d.score_pct],
        backgroundColor: ["rgba(61,122,74,0.15)", "rgba(154,110,32,0.15)", "rgba(44,36,22,0.12)"],
        borderColor:     ["#3D7A4A", "#9A6E20", "#2C2416"],
        borderWidth: 1.5,
        borderRadius: 4,
        borderSkipped: false,
      }],
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: { legend: { display: false } },
      scales: {
        y: {
          min: 0, max: 100,
          grid:  { color: "rgba(196,173,144,0.25)" },
          ticks: { color: "#A89070", font: { family: "'DM Mono'", size: 10 }, callback: v => `${v}%` },
          border: { display: false },
        },
        x: {
          grid:  { display: false },
          ticks: { color: "#7A6548", font: { family: "'DM Sans'", size: 11 } },
          border: { display: false },
        },
      },
    },
  });

  // Flagged words
  const fw = document.getElementById("flaggedWords");
  const fc = document.getElementById("flaggedCard");
  if (d.sensational_words.length) {
    fw.innerHTML = d.sensational_words
      .map(w => `<span class="chip">${w}</span>`)
      .join("");
    fc.style.display = "block";
  } else {
    fc.style.display = "none";
  }

  // Annotated text — replace [[...]] with highlighted spans
  const hl = d.highlighted.replace(
    /\[\[(.+?)\]\]/g,
    (_, m) => `<mark class="flag">${m}</mark>`
  );
  document.getElementById("annotatedText").innerHTML = hl;
}

// ── Keyboard shortcut ─────────────────────────────────────────────────────────
document.addEventListener("keydown", e => {
  if ((e.ctrlKey || e.metaKey) && e.key === "Enter") analyse();
});

// ── Health check ──────────────────────────────────────────────────────────────
window.addEventListener("load", async () => {
  try {
    const r = await fetch(API + "/api/health", { signal: AbortSignal.timeout(2000) });
    if (r.ok) setStatus("ready", "Ready");
    else       setStatus("error", "Error");
  } catch {
    setStatus("error", "Offline");
  }
});
