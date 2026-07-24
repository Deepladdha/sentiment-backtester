# Sentiment-Driven Algorithmic Trading Backtester

A backtesting engine that combines historical price data with news sentiment analysis to simulate and evaluate trading strategies. Built as a learning project to go from "can write Python" to "can build and reason about a real, tested, packaged software system."

**Status:** Phase 1 (Core) and Phase 2 (Data) complete, fully tested. Phase 3 (Strategies) and Phase 4 (Engine) not yet started.

---

## Table of Contents

1. [Why This Project Exists](#why-this-project-exists)
2. [Architecture Overview](#architecture-overview)
3. [Prerequisites & Setup](#prerequisites--setup)
4. [Phase 1: Core — The State Engine](#phase-1-core--the-state-engine)
5. [Phase 2: Data — Fetching & Caching](#phase-2-data--fetching--caching)
6. [Testing Philosophy](#testing-philosophy)
7. [Mistakes Made & Lessons Learned](#mistakes-made--lessons-learned)
8. [Known Limitations](#known-limitations)
9. [What's Next](#whats-next)

---

## Why This Project Exists

Most "learn to code" projects stop at "it runs." This one is deliberately built like production software would be: packaged properly, tested at every step, using precise financial data types, and designed so pieces can be swapped out (a different sentiment model, a different data source) without rewriting everything around them.

The goal isn't just "a backtester that works" — it's a project where every design decision can be explained and defended, because it was reasoned through, not copy-pasted.

---

## Architecture Overview

```
sentiment-backtester/
├── pyproject.toml          # Package metadata, dependencies, build config
├── .env.example             # Template for required environment variables
├── .env                      # Real secrets (gitignored, never committed)
├── .gitignore
├── README.md
├── src/
│   └── backtester/
│       ├── __init__.py
│       ├── core/
│       │   ├── __init__.py
│       │   ├── transaction.py     # Transaction dataclass + Action enum
│       │   ├── portfolio.py        # Portfolio state engine
│       │   └── exceptions.py       # Custom exception types
│       ├── data/
│       │   ├── __init__.py
│       │   ├── base.py             # Abstract DataSource contract
│       │   ├── price_source.py     # yfinance-backed price fetcher
│       │   ├── sentiment_source.py # NewsAPI + VADER sentiment fetcher
│       │   └── cache.py            # Local JSON caching layer
│       ├── strategies/             # (Phase 3 — not yet built)
│       ├── engine/                 # (Phase 4 — not yet built)
│       ├── metrics/                # (Phase 4 — not yet built)
│       └── api/                    # (stretch goal — not yet built)
├── tests/
│   ├── conftest.py           # Shared pytest fixtures
│   ├── test_portfolio.py
│   ├── test_price_source.py
│   ├── test_sentiment_source.py
│   └── test_cache.py
├── config/                    # (reserved for strategy/run configs)
├── notebooks/                  # (reserved for exploratory analysis)
└── scripts/                    # (reserved for CLI entry points)
```

**Why `src/` layout instead of a flat `backtester/` folder in root?**
If the package sat directly in the project root, `pytest` could accidentally import it straight off disk without it ever being properly installed — meaning tests could pass locally while hiding real packaging bugs. Putting it inside `src/` forces the only way to import `backtester` to be through a proper install (`pip install -e .`), so tests always run against the same thing a real user would get.

---

## Prerequisites & Setup

```bash
git clone <repo-url>
cd sentiment-backtester
python -m venv .venv
source .venv/Scripts/activate      # Windows Git Bash
# source .venv/bin/activate        # Mac/Linux
pip install -e ".[dev]"
cp .env.example .env               # then fill in NEWS_API_KEY
pytest tests/ -v
```

**Environment variables required** (see `.env.example`):
- `NEWS_API_KEY` — free key from [newsapi.org](https://newsapi.org/register). Free tier: 100 requests/day, articles limited to roughly the last 30 days.

---

## Phase 1: Core — The State Engine

### `core/transaction.py`

Defines two things:

- **`Action(Enum)`** — restricts a transaction's action to exactly `BUY` or `SELL`. Enums exist because plain string type hints (`action: str`) are *not enforced by Python at runtime* — they're only documentation for humans and tools like `mypy`. Without an enum, `Transaction(..., action="BANANA")` would be silently accepted.
- **`Transaction`** — an immutable (`@dataclass(frozen=True)`) record of a single trade: `ticker`, `quantity`, `price`, `timestamp`, `action`.

**Why `frozen=True`?** Past transactions should never change after the fact. If a bug elsewhere in the codebase accidentally tried to mutate a historical transaction, `frozen=True` turns that into an immediate, loud `FrozenInstanceError` — instead of silently corrupting historical data and producing a wrong backtest result with no error at all.

**Why `Decimal` instead of `float` for `price`?** Floats store numbers in binary, and most decimal fractions can't be represented exactly (`0.1 + 0.2 == 0.30000000000000004`). For money, where every cent must reconcile exactly, that imprecision compounds across thousands of trades. `Decimal` avoids this — but only if constructed correctly (see [Mistakes](#mistakes-made--lessons-learned) below).

**Why `__post_init__` validation?** Type hints alone don't stop someone from passing a raw string `"BUY"` instead of `Action.BUY` — Python accepts it silently, no error. `__post_init__` (a hook `@dataclass` calls automatically right after construction) adds a runtime `isinstance` check that raises `TypeError` immediately if `action` isn't a real `Action` member.

### `core/exceptions.py`

Two custom exception classes: `InsufficientFundsError`, `InsufficientHoldingsError`. Both inherit from `Exception`, contain no extra logic — the *name itself* is the point. This lets calling code catch specific failure categories precisely (`except InsufficientFundsError:`) instead of catching a generic `ValueError` and having to inspect the error message string to figure out what actually went wrong.

### `core/portfolio.py`

Holds `cash` (Decimal), `holdings` (dict of ticker → quantity), and `transaction_history` (a list of every successful `Transaction`, kept as an append-only audit log).

**Design decision — mutation + audit log, not pure event sourcing.** Two designs were considered:
- Pure event sourcing (derive current state by replaying the full transaction list every time) — correct but wasteful; recomputing history on every trade doesn't scale.
- Pure mutation (only track current `cash`/`holdings`, discard transaction records) — fast, but leaves no way to verify or debug how the portfolio arrived at its current state if something looks wrong.

The chosen design keeps `cash`/`holdings` as directly mutated state for speed, **and** appends every successful transaction to `transaction_history` purely as an audit trail — used later for equity curve plotting and correctness verification (you can always replay the log independently and confirm it matches current state).

**`execute(transaction)`** is the single method through which all state changes happen:
- On `BUY`: checks `cost > self.cash` → raises `InsufficientFundsError` if true; otherwise deducts cash, adds to holdings.
- On `SELL`: checks `quantity > current_holding` → raises `InsufficientHoldingsError` if true; otherwise adds cash, deducts holdings.
- Only appends to `transaction_history` **after** validation passes — a failed transaction never gets recorded, so the log only ever contains transactions that actually happened.

Uses `self.holdings.get(ticker, 0)` rather than `self.holdings[ticker]` — `.get()` returns a default value (`0`) instead of raising `KeyError` when a ticker has never been held before, which is the correct, expected state (zero shares), not an error condition.

---

## Phase 2: Data — Fetching & Caching

### `data/base.py`

`DataSource(ABC)` — an **abstract base class** with one abstract method: `fetch(ticker, start, end) -> pd.DataFrame`. Any subclass that doesn't implement `fetch()` cannot be instantiated at all — Python enforces this at the language level, not just by convention. This is what makes the plugin architecture (multiple interchangeable data sources sharing one contract) a hard guarantee rather than a hope that everyone remembers to implement the right method.

### `data/price_source.py`

`PriceDataSource(DataSource)` — wraps `yfinance`. Key steps inside `fetch()`:

1. Check the cache first (see `cache.py` below); return immediately on a hit.
2. `yf.download(ticker, start=start, end=end)` — returns a `pandas.DataFrame` with a **MultiIndex** column structure (`Price` level: Close/High/Low/Open/Volume; `Ticker` level underneath), because `yfinance` supports multi-ticker requests even though this project only ever requests one ticker at a time.
3. `raw_data.columns = raw_data.columns.get_level_values(0)` — flattens the MultiIndex down to simple column names by keeping only the first (`Price`) level.
4. Converts `Close`, `High`, `Low`, `Open` to `Decimal` (see precision note below). `Volume` is deliberately **left as `int64`** — it's a whole-number share count with no fractional/precision concern, and converting it to `Decimal` would add overhead and misleadingly imply it needs currency-grade precision.
5. Saves the result to cache, then returns it.

### `data/sentiment_source.py`

`SentimentDataSource(DataSource)` — fetches news headlines from NewsAPI's `/v2/everything` endpoint via raw `requests.get()` calls (unlike `yfinance`, there's no wrapper library handling HTTP for us here), then scores each headline's sentiment using **VADER** (`vaderSentiment`), a rule-based/lexicon sentiment scorer.

Key implementation details:
- `__init__` loads the API key (via `python-dotenv` + `os.getenv`) and creates one reusable `SentimentIntensityAnalyzer()` instance — done once per object, not once per `fetch()` call, since it's a stateless, reusable tool.
- `response.raise_for_status()` — immediately raises `HTTPError` on any non-2xx status code, before the code tries to access `data["articles"]` (which wouldn't exist on a failed request). Fail loudly, at the actual point of failure, rather than crashing later with a confusing, unrelated error.
- Extracts only `title` (scored for sentiment), `publishedAt` (needed to later align sentiment with price data by date), and includes `ticker` in each record (added as a self-describing field, useful when inspecting cached files directly).
- Deliberately ignores `content` (NewsAPI's free tier truncates it) and `description` (kept out for v1 simplicity — a reasonable future upgrade, not a mistake).

### `data/cache.py`

`Cache` — a simple local-file (JSON) cache keyed by `ticker + start date + end date`. Exists because:
- `yfinance` calls are slower than necessary if repeated for identical requests during development.
- NewsAPI's free tier caps at **100 requests/day** — without caching, iterative development/testing would burn through the daily quota quickly.

**Design:** `_build_key()` and `_file_path()` are private (underscore-prefixed) helper methods, called only from within `get()`/`save()` — never from outside the class. `PriceDataSource`/`SentimentDataSource` call `cache.get(ticker, start, end)` and `cache.save(ticker, start, end, df)` directly; they have **zero knowledge** that the cache uses string keys or JSON files internally. This is encapsulation — if the caching backend were swapped later (e.g., to SQLite), nothing outside `Cache` would need to change.

**Each `DataSource` uses its own cache subdirectory** (`.cache/prices/`, `.cache/sentiment/`) — see [Mistakes](#mistakes-made--lessons-learned) for why this was necessary, not optional.

---

## Testing Philosophy

Every component has automated tests using `pytest`, following two consistent principles:

1. **Never let tests hit real external services** (Yahoo Finance, NewsAPI). Real-API tests are risky because a failure could mean "your code has a bug" *or* "the network/API was briefly down/rate-limited" — indistinguishable without investigation. `unittest.mock.patch` replaces the real `yf.download` / `requests.get` calls with controlled fake objects during tests, so test failures only ever mean "your logic is wrong."
2. **Assert on behavior, not on fragile exact values.** E.g., sentiment tests assert `score < 0` for negative headlines, not an exact float like `-0.6597` — VADER's internal scoring could change between library versions, and that's not a bug in *this* codebase. Similarly, `Cache` round-trip tests check `len(result) == 1` rather than exact `Decimal` equality, since JSON serialization degrades `Decimal` back into `float` (see Known Limitations).

`conftest.py` holds shared fixtures (like a fresh `Portfolio` per test) so setup code isn't duplicated across every test function, and pytest's `tmp_path` fixture is used for `Cache` tests to avoid polluting the real `.cache/` directory with test data.

**Current test count:** 11 passing, covering `Portfolio` (buy/sell success and failure paths, transaction log integrity), `PriceDataSource` (Decimal conversion correctness), `SentimentDataSource` (headline parsing and sentiment scoring), and `Cache` (save/get round-trip, missing-key behavior).

---

## Mistakes Made & Lessons Learned

Kept deliberately, because catching and understanding these was most of the actual learning.

| # | Mistake | Why it happened | Fix / Lesson |
|---|---------|------------------|---------------|
| 1 | `pyproject.toml` had `optionl-dependencies` (typo) | Simple typo | pip's error message named the exact bad key — read the *last lines* of a long traceback first, that's where the real info is |
| 2 | `pip install -e .` installed into global Python, not `.venv` | Command run before venv was actually active in that terminal session | Always confirm with `which python` before trusting an install; venv activation only lasts one terminal session |
| 3 | `python3` inside an activated venv launched an unrelated global Python 3.11 install | On Windows, `venv` only creates `python.exe`, not `python3.exe` — `python3` silently fell through to PATH | Always use plain `python` inside an activated venv on Windows |
| 4 | `import backtester` returned `__file__ = None` | No `__init__.py` files existed yet — Python treated folders as implicit "namespace packages" | Every package folder needs an explicit `__init__.py` to be a real, well-defined package |
| 5 | `Transaction` referenced `Action` before `Action` was defined in the file | Class order matters — Python reads top to bottom | Define/import anything before the line that references it |
| 6 | Passing a raw string `"BUY"` instead of `Action.BUY` was silently accepted | Type hints (`action: Action`) are not enforced by Python at runtime | Added `__post_init__` validation to catch this at construction time, not later |
| 7 | `Decimal(50.5)` (from a float) produced garbage precision (`150.56219482421875`-style values) | Converting a float to Decimal preserves the float's *existing* binary imprecision — it doesn't fix it | Always construct `Decimal` from a **string**: `Decimal(str(round(x, 2)))`, never `Decimal(float_value)` directly |
| 8 | `git restore --staged` failed with `fatal: could not resolve HEAD` | No commits existed yet — there was no prior commit state to "restore" to | With zero commits, use `git rm --cached` to unstage instead |
| 9 | `src/sentiment_backtester.egg-info/` got staged for commit | Auto-generated by `pip install -e .`; not something to version control | Any auto-generated build artifact (`egg-info`, `__pycache__`, `.venv`) belongs in `.gitignore`, discovered as it appears |
| 10 | `.gitignore` had `.egg-info/` instead of `*.egg-info/` | Missing wildcard — matched a folder literally named `.egg-info`, not `sentiment_backtester.egg-info` | Small syntax details in `.gitignore` patterns matter; verify the pattern actually matches before trusting it |
| 11 | Mock patch path used `src.backtester...` instead of `backtester...` | Confused the on-disk folder path with the actual Python import path | `src/` is a folder convention only — it is never part of the real importable package path |
| 12 | `requests(...)` instead of `requests.get(...)` | Typo — called the module itself instead of a function inside it | `TypeError: 'module' object is not callable` almost always means a missing `.function_name` |
| 13 | `response.json` instead of `response.json()` | Missing parentheses — referenced the method object instead of calling it | Always double check `()` on method calls, especially when chaining |
| 14 | NewsAPI request for June 2026 data returned `426 Upgrade Required` | Free tier only allows roughly the last 30 days of historical articles; request was for dates outside that window | Sentiment data has a much narrower usable history than price data — a real constraint the backtester's design must account for |
| 15 | VADER scored "Apple stock surges after record-breaking earnings" as perfectly neutral (`compound: 0.0`) | VADER's lexicon was built for everyday/social-media language, not financial terminology — words like "surges" or "earnings beat" carry no sentiment weight in its dictionary | Documented as a known limitation; FinBERT (a finance-trained model) is the planned future upgrade, deliberately deferred until the full pipeline works end-to-end |
| 16 | `Cache` defaulted to the same `.cache/` folder for both `PriceDataSource` and `SentimentDataSource` | Both used identical default `cache_dir` and identical key logic (`ticker_start_end`) — a price fetch and sentiment fetch for the same ticker/dates would collide on the exact same file | **Caught through code review, not a crash** — each `DataSource` now uses its own cache subdirectory (`.cache/prices/`, `.cache/sentiment/`) |
| 17 | `Decimal` values saved to the cache come back as `float` after a `get()` | JSON has no native `Decimal` type — `to_json()`/`read_json()` silently round-trips through plain JSON numbers, losing the original Python type | Documented as a known limitation (see below); tests deliberately avoid asserting exact `Decimal` equality on cached data as a result |

---

## Known Limitations

These are understood, not accidental — each one has a clear reason and a clear path to fixing it later:

- **Sentiment data has a ~30-day historical window** (NewsAPI free tier), while price data (`yfinance`) has years of history. Any strategy combining both will need to explicitly handle dates where sentiment data doesn't exist, or the project will need a paid NewsAPI tier eventually.
- **VADER is a weak fit for financial language.** It correctly catches strongly emotional words (lawsuit, stolen, crushed) but misses financial-specific signals (surged, earnings beat, price hike). Planned fix: swap in FinBERT once the full pipeline (Phases 3–4) works end-to-end with VADER as a baseline — this also gives a clean "before/after" comparison to talk about.
- **`Decimal` precision degrades to `float` through the JSON cache.** Since JSON has no native decimal type, any price read back from cache loses `Decimal`'s exactness guarantee. Not yet fixed — a future improvement would explicitly re-cast price columns to `Decimal` inside `Cache.get()` after reading.

---

## What's Next

- **Phase 3 — Strategies:** an abstract `Strategy` base class (same ABC pattern as `DataSource`) with concrete implementations (`SentimentThresholdStrategy`, later `MovingAverageCrossover`), designed as swappable plugins.
- **Phase 4 — Engine:** `BacktestEngine` ties `Portfolio` + `DataSource`s + `Strategy` together into a day-by-day simulation loop, with careful attention to avoiding lookahead bias (never letting the strategy see data from the future relative to the simulated "current" date).
- **Metrics:** Sharpe ratio, max drawdown, CAGR, win rate — pure functions over the resulting equity curve.
- **Stretch goals:** FastAPI layer exposing the backtester as a service; FinBERT sentiment upgrade; CI via GitHub Actions.
