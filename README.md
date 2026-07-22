# 🛒 Blinkit Discovery Engine

> **Nextleap Graduation Project**  
> An AI-powered monthly review analysis system that helps Blinkit understand why users don't explore new categories — and what to do about it.

---

## 🤔 What Problem Does This Solve?

Blinkit users are stuck in a habit loop. They open the app, buy the same groceries, and leave — never discovering high-margin categories like **Pet Care, Beauty, Electronics, Home Needs, or Baby Care**.

This system automatically analyzes thousands of app reviews, social posts, and support tickets every month to answer **8 key product questions**:

---

## ❓ The 8 Questions This System Answers

| # | Question | Answered By |
|---|----------|------------|
| 1 | **Why do users repeatedly buy from the same categories?** | Habit & Velocity Barrier analysis |
| 2 | **What prevents users from exploring new categories?** | UX Friction & Invisible Inventories analysis |
| 3 | **How do users discover products today?** | Cluster analysis of discovery-related reviews |
| 4 | **What role do habits play in shopping behavior?** | Sentiment patterns in recurring grocery reviews |
| 5 | **What information do users need before trying a new category?** | Trust & Information Gap analysis |
| 6 | **What frustrations emerge repeatedly?** | 1.5% volume threshold flagging across all sources |
| 7 | **Which user segments are more likely to experiment?** | Segment Propensity cluster mapping |
| 8 | **What unmet needs emerge consistently across discussions?** | Cross-platform corroboration of insight clusters |

> **These answers are automatically computed by the AI backend every month and displayed in the dashboard for anyone to explore.**

---

## 🚀 How to Run the Dashboard

### Prerequisites
```bash
# Make sure Python 3.12+ is installed
python --version

# Install dependencies
pip install -r requirements.txt
# or if using uv:
uv sync
```

### Launch the Dashboard
```bash
streamlit run src/dashboard/app.py
```

Then open your browser at `http://localhost:8501`

---

## 📊 What You'll See in the Dashboard

Once you open the dashboard, you'll find **5 sections**:

### 1. ❓ Questions & Answers Page *(Start Here)*
Each of the 8 questions above is shown as a card with:
- The AI-generated answer based on this month's reviews
- The relevant user quotes that support the answer
- The confidence score and source breakdown

### 2. 📊 Pillar Scores
Four horizontal bar charts showing how strongly each discovery barrier showed up this month:
- 🔁 Habit & Velocity Barrier
- 🔍 Trust & Information Gap
- 🖥️ UX Friction & Invisible Inventories
- 🎯 Segment Propensity

### 3. 🏷️ Top Themes
Insight cards for each discovered cluster — ranked by confidence — with real user quotes and actionable recommendations.

### 4. 📈 Monthly Trend
A line chart showing how the pillar scores have changed across all past monthly runs. See whether problems are getting better or worse over time.

### 5. 💬 Review Feed
Browse the raw reviews that fed into the analysis. Filter by:
- **Source**: App Store, Play Store, Reddit, Twitter, Support Logs
- **Star Rating**: 1★ to 5★
- **Category**: Pet Care, Beauty, Electronics, Home, Baby Care
- **Month**: Any past run
- **Search**: Free-text search across all review text

---

## 🏗️ How the System Works (For Developers)

```
┌─────────────────────────────────────────────────────────────────┐
│                    MONTHLY AUTOMATED PIPELINE                    │
│                                                                  │
│  📥 INGEST          🧠 PROCESS         ✅ VALIDATE              │
│  App Store    →    PII Scrub    →    4 Checkpoints:             │
│  Play Store   →    Sentiment   →    • Cross-platform            │
│  Reddit       →    NER         →    • 1.5% volume rule          │
│  Twitter      →    Clustering  →    • Dual-model verify         │
│  Support Logs →    LLM Labels  →    • Reality check             │
│                                           ↓                      │
│  📬 DELIVER                        📊 DASHBOARD                  │
│  Google Docs MCP  ←── Validated ──→  Streamlit UI               │
│  Gmail MCP            Insights        (this app)                 │
└─────────────────────────────────────────────────────────────────┘
```

The backend runs automatically on the **1st Monday of every month** and saves results to `data/insights/validated_YYYY-MM.json`. The dashboard reads from these files — so it always shows the latest available data without you needing to do anything.

---

## 📁 Project Structure

```
Nextleap Graduation project Blinkit/
│
├── src/
│   ├── ingestion/       ← Collects reviews from all sources
│   ├── processing/      ← Cleans text, removes PII, extracts sentiment
│   ├── insights/        ← Clusters reviews and labels themes with LLM
│   ├── validation/      ← 4-checkpoint quality control
│   ├── delivery/        ← Builds report and email
│   ├── mcp/             ← Delivers to Google Docs + Gmail via MCP
│   ├── dashboard/       ← Streamlit web dashboard (this app)
│   └── scheduler/       ← Monthly automated trigger
│
├── data/
│   ├── raw/             ← Raw ingested reviews (one file per source/month)
│   ├── processed/       ← Cleaned + sentiment-tagged reviews
│   ├── insights/        ← Validated insight clusters (dashboard reads from here)
│   └── reports/         ← Final Markdown reports + email HTML
│
├── docs/
│   ├── problemstatement.md    ← What problem we're solving and why
│   ├── implementation_plan.md ← Phase-by-phase build plan (5 phases, 17 weeks)
│   └── architecture.md        ← Full technical architecture (6 layers)
│
├── README.md            ← You are here
└── .env                 ← API keys (not committed — ask project owner)
```

---

## 🔑 Required API Keys (for Backend)

> The dashboard works **without any API keys** — it only reads existing data files.  
> API keys are only needed to run the ingestion pipeline.

| Key | Where to get it | Used for |
|-----|----------------|---------|
| `OPENAI_API_KEY` | platform.openai.com | LLM theme labelling |
| `REDDIT_CLIENT_ID` | reddit.com/prefs/apps | Reddit ingestion |
| `TWITTER_BEARER_TOKEN` | developer.twitter.com | Twitter ingestion |
| `GOOGLE_MCP_CREDS` | Google Cloud Console | Google Docs + Gmail via MCP |

Copy `.env.example` to `.env` and fill in your keys.

---

## 🧪 Running Tests

```bash
# Run all tests
pytest tests/

# Run a specific test file
pytest tests/test_validation.py -v

# Run with coverage report
pytest tests/ --cov=src
```

---

## 📖 Documentation

| Document | What's Inside |
|----------|--------------|
| [Problem Statement](docs/problemstatement.md) | The business problem, the 4 discovery pillars, and the system blueprint |
| [Implementation Plan](docs/implementation_plan.md) | 5-phase, 17-week build plan with tasks and exit criteria for each phase |
| [Architecture](docs/architecture.md) | 6-layer technical architecture with diagrams for every component |

---

## 👤 Project Author

**Nextleap Graduation Project**  
Built as part of the Nextleap Product Management program.

---

> **New to this project?** Start by opening the dashboard (`streamlit run src/dashboard/app.py`) and going to the **"❓ Questions & Answers"** page — it will show you exactly what the system has discovered this month in plain English.
