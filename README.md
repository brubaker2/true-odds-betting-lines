# True Odds Betting Lines

A lightweight Flask app that pulls sportsbook odds from [The Odds API](https://the-odds-api.com) and calculates **vig-free "true odds"** for MLB, NFL, NCAAF, NHL, and NBA — displayed in American odds format on a mobile-friendly dashboard.

**Live:** https://true-odds-betting-lines.onrender.com

---

## What it does

Sportsbooks bake a margin (the "vig" or "juice") into every line, so posted odds always imply more than 100% total probability. This app strips that margin out to estimate what each side's fair price would be in an efficient market.

For each game it shows three markets:

- **Moneyline** (h2h)
- **Point spread**
- **Total** (over/under)

The away team is always listed first and the home team second, matching the `Away @ Home` header on each card.

---

## How true odds are calculated

1. **Fetch** all US-region bookmaker lines for the sport from The Odds API.
2. **Filter by vig.** For each book's two-sided market, convert both prices to implied probability and sum them. Only books whose total is **under 105.5%** (i.e. vig < 5.5%) are used. Everything else is discarded.
3. **Pick the consensus line** (spreads and totals only). Count how many qualifying books offer each point value, then keep only the most common one. Books offering a different number are excluded — you can't average "Over 5.5" with "Over 6.5", they're different bets.
4. **Half-numbers only.** Whole-number lines (6.0, -3, +7) are skipped entirely so every displayed line is a clean win/lose with no push.
5. **Average implied probabilities**, not the odds themselves. American odds are nonlinear, so averaging `-200` and `-180` directly gives a different — and wrong — answer versus converting each to probability first.
6. **Normalize** the two averaged probabilities so they sum to exactly 100%, then convert back to American odds.

If no book clears the vig filter for a given market, that cell reads **"Filtered out."** This is common on lopsided moneylines (a -3000 favorite almost always carries more than 5.5% vig) and is expected behavior, not an error.

---

## Project structure

```
.
├── app.py                 # Flask server + API proxy
├── requirements.txt       # Python dependencies
├── Procfile               # Start command for deployment
└── static/
    └── index.html         # Entire frontend (HTML/CSS/JS, no build step)
```

The frontend is a single self-contained file with no framework or bundler. All odds math lives in the `<script>` block at the bottom.

---

## Why a backend proxy?

The Odds API doesn't send CORS headers, so a browser can't call it directly from a static page — the request fails before it leaves the browser. `app.py` makes the call server-side and relays the JSON, which also keeps the API key off the client entirely.

---

## Setup

### Requirements

- Python 3.9+
- A free API key from [the-odds-api.com](https://the-odds-api.com)

### Run locally

```bash
pip install -r requirements.txt
export ODDS_API_KEY=your_key_here      # Windows: set ODDS_API_KEY=your_key_here
python app.py
```

Open http://localhost:5000

### Deploy to Render

1. Push this repo to GitHub.
2. In Render, create a **New Web Service** and connect the repo.
3. Settings:
   - **Runtime:** Python 3
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `gunicorn app:app`
4. Under **Environment**, add:
   - Key: `ODDS_API_KEY`
   - Value: your API key
5. Deploy. Confirm **Auto-Deploy** is set to **Yes** so future commits redeploy automatically.

On iPhone, open the Render URL in Safari and use **Share → Add to Home Screen** to run it like an app.

---

## API credit usage

The free tier allows **500 credits/month**. Each fresh load costs **3 credits per sport** — one for each of `h2h`, `spreads`, and `totals`.

Two caching layers keep this down:

- **In-memory** — switching between tabs you've already loaded costs nothing.
- **localStorage** — a sport's data is reused for **15 minutes** across page reloads and browser restarts. Cached loads show `cached` in the status bar instead of a credit count.

A full sweep of all five tabs is 15 credits, so roughly 33 sweeps per month on the free tier before re-checks start drawing down. Adjust `CACHE_TTL` in `static/index.html` to trade freshness for credits.

---

## Configuration

Both constants are at the top of the `<script>` block in `static/index.html`:

| Constant | Default | Effect |
|---|---|---|
| `MAX_VIG` | `1.055` | Vig ceiling for including a book. Lower = stricter, fewer books, more "Filtered out." |
| `CACHE_TTL` | `15 * 60 * 1000` | How long cached odds stay valid, in milliseconds. |

To add a sport, add one button to the header with the matching Odds API sport key — the rest of the pipeline is sport-agnostic:

```html
<button class="sport-btn" data-sport="basketball_ncaab">NCAAB</button>
```

---

## Notes and limitations

- **Render's free tier sleeps** after ~15 minutes of inactivity. The first request afterward takes 20–30 seconds to wake the service.
- **Only US-region books** are queried. Pinnacle — widely treated as the sharpest reference — isn't available in the US region and isn't included.
- **True odds are an estimate**, not ground truth. They reflect the consensus of the books that cleared the vig filter at the moment of the pull, nothing more.
- **The API key must never be committed.** It's read from the `ODDS_API_KEY` environment variable; there's no fallback value in the source.

---

## Disclaimer

This is a personal tool for analyzing publicly posted odds. It doesn't place bets, offer betting advice, or predict outcomes. Sports betting carries real financial risk, and no odds model changes that. Follow the laws where you live, and if gambling stops feeling like it's under control, the [National Problem Gambling Helpline](https://www.ncpgambling.org/help-treatment/) is at 1-800-522-4700.
