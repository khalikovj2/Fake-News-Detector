# Verifai — News Credibility Checker

> *An AI-powered fake news detection engine that scores the credibility of any text in under a second.*

![Python](https://img.shields.io/badge/Python-3.10+-2C2416?style=flat-square&labelColor=F7F3EC)
![Flask](https://img.shields.io/badge/Flask-3.0-2C2416?style=flat-square&labelColor=F7F3EC)
![scikit-learn](https://img.shields.io/badge/scikit--learn-1.4-2C2416?style=flat-square&labelColor=F7F3EC)
![License](https://img.shields.io/badge/License-MIT-2C2416?style=flat-square&labelColor=F7F3EC)

---

## Overview

**Verifai** combines a Logistic Regression classifier trained on TF-IDF features with 30+ hand-crafted linguistic pattern rules to produce a credibility score from 0 to 100 for any piece of text — no API keys, no cloud services, no GPU required.

Paste a headline or article and get back:

- **Credibility score** — 0 (fake) to 100 (credible)
- **Verdict** — Likely Credible / Uncertain / Likely Fake
- **Clickbait pattern count** — exclamation abuse, ALL CAPS, sensational phrases
- **Credible marker count** — citations, expert references, institutional language
- **Sensational word flags** — highlighted directly in the original text
- **Score breakdown chart** — ML score vs pattern score vs final score

---

## Demo

```
Fake:   "SHOCKING!!! Scientists EXPOSED covering up MIRACLE cure!!!"  →  Score: 12%  ✕ Likely Fake
Real:   "Researchers at MIT published findings in Nature Energy…"     →  Score: 84%  ✓ Likely Credible
Mixed:  "Officials confirmed an unusual incident near the town hall…" →  Score: 51%  ~ Uncertain
```

---

## Tech Stack

| Layer         | Technology                             |
|---------------|----------------------------------------|
| Backend       | Python 3.10+ · Flask · Flask-CORS      |
| ML Model      | scikit-learn Logistic Regression       |
| Features      | TF-IDF Vectorizer (unigrams + bigrams) |
| Pattern Rules | 30+ regex linguistic rules             |
| Frontend      | Vanilla HTML · CSS · JavaScript        |
| Charts        | Chart.js 4.4                           |
| Typography    | Playfair Display · DM Sans · DM Mono   |

---

## Project Structure

```
fake_news_detector/
├── backend/
│   └── app.py              ← Flask API + ML pipeline + pattern rules
├── frontend/
│   ├── index.html          ← Warm cream minimalist UI
│   ├── css/
│   │   └── style.css       ← Design system
│   └── js/
│       └── app.js          ← API calls + Chart.js rendering
├── requirements.txt
└── README.md
```

---

## Getting Started

**1. Clone the repository**

```bash
git clone https://github.com/khalikovj2/Fake-News-Detector.git
cd Fake-News-Detector
```

**2. Install dependencies**

```bash
pip install -r requirements.txt
```

**3. Run the app**

```bash
python backend/app.py
```

The browser opens automatically at **http://localhost:5001**

---

## How the Model Works

```
Input Text
    │
    ├── TF-IDF Vectorizer (unigrams + bigrams, 500 features)
    │       │
    │       └── Logistic Regression → ML credibility probability (65% weight)
    │
    ├── Regex Pattern Matcher
    │       ├── 20+ clickbait patterns  (SHOCKING, YOU WON'T BELIEVE, !!!, ALL CAPS...)
    │       ├── 15+ credible markers    (according to, researchers, study, published...)
    │       └── Sensational word list   (explosive, bombshell, miracle, exposed...)
    │               │
    │               └── Rule-based score (35% weight)
    │
    └── Weighted combination → Final Score (0–100)
```

**Thresholds:**
- Score ≥ 70  →  ✓ Likely Credible
- Score 45–69 →  ~ Uncertain  
- Score < 45  →  ✕ Likely Fake / Clickbait

---

## API Endpoints

```
POST /api/analyze     { "text": "..." }   → Full analysis JSON
GET  /api/health                          → { "status": "ok" }
GET  /                                    → Serves frontend
```

**Example request:**

```bash
curl -X POST http://localhost:5001/api/analyze \
  -H "Content-Type: application/json" \
  -d '{"text": "Scientists at MIT published new research on solar energy efficiency."}'
```

**Example response:**

```json
{
  "score": 0.82,
  "score_pct": 82.0,
  "verdict": "Likely Credible",
  "clickbait_patterns": 0,
  "credible_markers": 2,
  "sensational_words": [],
  "word_count": 12
}
```

---

## Keyboard Shortcut

Press **Ctrl + Enter** to run analysis instantly from anywhere on the page.

---

## Known Limitations

- Trained on a small representative dataset — designed for demonstration purposes
- Does not detect subtle misinformation that uses credible-sounding language
- English language only
- Sarcasm and irony are not reliably detected by rule-based systems

---

## Author

**Javokhirbek Khalikov**  
Student ID: 32223879  
Dankook University · Mobile Systems Engineering  
Capstone Design (MS) · Prof. Jaeyeon Park

---

*For educational purposes only. Not intended as a definitive fact-checking tool.*
