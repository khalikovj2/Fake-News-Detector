"""
app.py — Fake News Detector Backend
Run: python backend/app.py
"""
import os, re, string, threading, webbrowser
from collections import Counter
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
import numpy as np

BASE_DIR     = os.path.dirname(os.path.abspath(__file__))
FRONTEND_DIR = os.path.abspath(os.path.join(BASE_DIR, "..", "frontend"))

app = Flask(__name__, static_folder=FRONTEND_DIR, static_url_path="")
CORS(app)

# ── Clickbait / fake news linguistic patterns ─────────────────────────────────
CLICKBAIT_PATTERNS = [
    r'\byou won\'t believe\b', r'\bshocking\b', r'\bblew my mind\b',
    r'\bmust see\b', r'\bgoing viral\b', r'\bbreaking\b', r'\bexclusive\b',
    r'\bsecret\b', r'\bthey don\'t want you\b', r'\bwake up\b',
    r'\bhoax\b', r'\bconspiracy\b', r'\bfake\b', r'\blies\b',
    r'\bmisinformation\b', r'\bcover.?up\b', r'\bsuppressed\b',
    r'\bunbelievable\b', r'\bimpossible\b', r'\bmiracle\b',
    r'!\s*!', r'\?{2,}', r'[A-Z]{4,}',
]

CREDIBLE_MARKERS = [
    r'\baccording to\b', r'\bresearchers\b', r'\bstudy\b', r'\bscientists\b',
    r'\buniversity\b', r'\bjournal\b', r'\bpublished\b', r'\bstatistics\b',
    r'\bdata shows\b', r'\bevidence\b', r'\bexperts say\b', r'\breport\b',
    r'\bofficial\b', r'\bgovernment\b', r'\bspokesperson\b',
]

SENSATIONAL_WORDS = {
    'shocking', 'explosive', 'bombshell', 'stunning', 'outrageous',
    'disgusting', 'terrifying', 'incredible', 'unbelievable', 'amazing',
    'devastating', 'catastrophic', 'apocalyptic', 'insane', 'crazy',
    'ridiculous', 'absurd', 'exposed', 'revealed', 'leaked',
}

# ── Training data (representative samples for demo) ───────────────────────────
TRAIN_TEXTS = [
    # Real news samples
    "Scientists at MIT published new research showing climate change affects crop yields",
    "The Federal Reserve raised interest rates by 25 basis points according to officials",
    "A study published in Nature found new evidence linking exercise to brain health",
    "Government officials confirmed the policy change after weeks of negotiations",
    "Researchers at Stanford University discovered a new treatment for diabetes",
    "The World Health Organization released updated guidelines for vaccination schedules",
    "Economic data released Tuesday showed unemployment fell to its lowest level in years",
    "A spokesperson for the company confirmed the merger pending regulatory approval",
    "Scientists discovered evidence of water ice on the lunar surface according to NASA",
    "The Supreme Court issued a ruling on the landmark case after months of deliberation",
    "University researchers published findings on the long-term effects of sleep deprivation",
    "The central bank announced new monetary policy measures to combat inflation",
    "A peer-reviewed study confirmed the drug's effectiveness in clinical trials",
    "Officials released crime statistics showing a decline in urban areas nationwide",
    "The environmental agency reported air quality improvements in major cities this year",
    # Fake news samples
    "You won't believe what they found!!! SHOCKING secret the government is hiding from you",
    "WAKE UP!!! Scientists EXPOSED covering up miracle cure that DESTROYS cancer overnight",
    "BREAKING: Unbelievable hoax revealed, they lied to us about EVERYTHING this whole time",
    "INSANE conspiracy blown wide open, celebrities drinking children's blood EXPOSED!!!",
    "This miracle berry DESTROYS diabetes in 3 days doctors DON'T want you to know",
    "SHOCKING truth about vaccines they are suppressing, share before they DELETE this",
    "You won't believe what this politician did, BOMBSHELL leaked footage going viral NOW",
    "INCREDIBLE cover-up exposed, the deep state has been lying about aliens for 50 years",
    "MUST SEE: Billionaire accidentally reveals secret to making millions overnight guaranteed",
    "Scientists BAFFLED by this one weird trick that reverses aging completely overnight",
    "EXPLOSIVE revelation, they have been putting chemicals in water to control minds",
    "This is INSANE they are hiding the cure for cancer to make more money from patients",
    "BREAKING BOMBSHELL whistleblower exposes everything you were never supposed to know",
    "Unbelievable miracle food destroys all disease doctors and big pharma HATE this",
    "SHOCKING video going viral proves moon landing was completely staged and faked",
]
TRAIN_LABELS = [1]*15 + [0]*15  # 1=credible, 0=fake/clickbait

vectorizer = TfidfVectorizer(ngram_range=(1,2), max_features=500, stop_words='english')
X_train    = vectorizer.fit_transform(TRAIN_TEXTS)
clf        = LogisticRegression(max_iter=1000, C=1.0)
clf.fit(X_train, TRAIN_LABELS)


def analyse_text(text):
    text = text.strip()
    if len(text.split()) < 3:
        return {"error": "Text too short. Please enter a headline or paragraph."}

    # ML credibility score
    X      = vectorizer.transform([text])
    proba  = clf.predict_proba(X)[0]
    ml_score = float(proba[1])  # probability of being credible

    # Pattern scoring
    tl     = text.lower()
    cb_hits   = [p for p in CLICKBAIT_PATTERNS  if re.search(p, tl, re.I)]
    cred_hits = [p for p in CREDIBLE_MARKERS    if re.search(p, tl, re.I)]
    words     = set(re.findall(r'\b\w+\b', tl))
    sens_hits = list(words & SENSATIONAL_WORDS)

    # Combine ML + rule scores
    pattern_score = 0.5
    pattern_score -= len(cb_hits)   * 0.06
    pattern_score += len(cred_hits) * 0.07
    pattern_score -= len(sens_hits) * 0.05
    pattern_score  = max(0.0, min(1.0, pattern_score))

    final_score = (ml_score * 0.65 + pattern_score * 0.35)
    final_score = round(max(0.0, min(1.0, final_score)), 4)

    if   final_score >= 0.70: verdict = "Likely Credible"
    elif final_score >= 0.45: verdict = "Uncertain"
    else:                      verdict = "Likely Fake / Clickbait"

    # Highlight suspicious phrases
    highlighted = text
    for p in CLICKBAIT_PATTERNS:
        highlighted = re.sub(p, lambda m: f"[[{m.group()}]]", highlighted, flags=re.I)

    return {
        "score":        final_score,
        "score_pct":    round(final_score * 100, 1),
        "verdict":      verdict,
        "clickbait_patterns": len(cb_hits),
        "credible_markers":   len(cred_hits),
        "sensational_words":  sens_hits[:8],
        "highlighted":        highlighted,
        "word_count":         len(text.split()),
        "features": {
            "ml_score":      round(ml_score * 100, 1),
            "pattern_score": round(pattern_score * 100, 1),
        }
    }


@app.route("/")
def index(): return send_from_directory(FRONTEND_DIR, "index.html")

@app.route("/css/<path:f>")
def css(f): return send_from_directory(os.path.join(FRONTEND_DIR,"css"), f)

@app.route("/js/<path:f>")
def js(f):  return send_from_directory(os.path.join(FRONTEND_DIR,"js"), f)

@app.route("/api/analyze", methods=["POST"])
def analyze():
    data = request.get_json(silent=True) or {}
    text = data.get("text","").strip()
    if not text: return jsonify({"error":"No text provided."}), 400
    return jsonify(analyse_text(text))

@app.route("/api/health")
def health(): return jsonify({"status":"ok"})


def open_browser():
    import time, subprocess, sys
    time.sleep(1.5)
    url = "http://localhost:5001"
    try:
        if sys.platform=="win32": os.startfile(url); return
    except: pass
    try:
        if sys.platform=="win32": subprocess.Popen(["cmd","/c","start",url]); return
    except: pass
    try: webbrowser.open_new_tab(url)
    except: pass

if __name__ == "__main__":
    print("\n" + "="*50)
    print("  FAKENEWS DETECTOR  —  http://localhost:5001")
    print("="*50 + "\n")
    threading.Thread(target=open_browser, daemon=True).start()
    app.run(debug=False, port=5001, host="0.0.0.0", use_reloader=False)
