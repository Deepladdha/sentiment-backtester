# Sentiment-Driven Algorithmic Trading Backtester

A Python-based framework for backtesting trading strategies driven by news and social media sentiment. This backtester allows you to simulate trades, manage a virtual portfolio, and compute performance metrics using historical market data and sentiment signals.

## Project Structure

The project follows a standard production-ready Python layout:

```text
sentiment-backtester/
├── src/
│   └── backtester/
│       ├── core/           # Core models (Transaction, Portfolio, Exceptions)
│       ├── strategies/     # Trading strategy definitions (e.g., SentimentStrategy)
│       ├── engine/         # Execution engine to run the backtest loop
│       ├── data/           # Market data fetchers and sentiment parsers
│       ├── metrics/        # Performance calculators (Sharpe Ratio, Drawdown, etc.)
│       └── api/            # API endpoints or interface wrapper (if needed)
├── tests/                  # Unit and integration tests (using pytest)
├── pyproject.toml          # Project configuration, dependencies, and metadata
└── README.md               # This file
```

## Features Implemented So Far

*   **Portfolio Management (`backtester.core.portfolio`):** Handles cash, tracks active stock holdings, and executes buy/sell transactions.
*   **Transaction Models (`backtester.core.transaction`):** Dataclass representations of individual trades with price, quantity, timestamp, and action type (BUY/SELL).
*   **Error Prevention (`backtester.core.exceptions`):** Prevents executing trades that exceed cash limits or attempt to sell shares not currently owned.

## Setup and Installation

### 1. Prerequisites
Make sure you have **Python 3.10 or higher** installed.

### 2. Create a Virtual Environment
In your terminal, navigate to the root directory and create a virtual environment:
```bash
python -m venv .venv
```

Activate the virtual environment:
*   **Windows (PowerShell):**
    ```powershell
    .venv\Scripts\Activate.ps1
    ```
*   **Windows (CMD):**
    ```cmd
    .venv\Scripts\activate.bat
    ```
*   **macOS / Linux:**
    ```bash
    source .venv/bin/activate
    ```

### 3. Install Dependencies
Install the package in editable mode along with its development dependencies:
```bash
pip install -e .[dev]
```
*(This looks at `pyproject.toml` and installs libraries like `pandas`, `numpy`, `yfinance`, and dev tools like `pytest`.)*

## Running Tests

To run the unit tests in verbose mode:
```bash
pytest -v
```

To run a specific test file:
```bash
pytest tests/test_portfolio.py -v
```

## Next Steps for Development

As you learn and build out this project, you can focus on these next major pieces:
1.  **Data Fetcher (`backtester/data`):** Use `yfinance` to download historical stock prices.
2.  **Strategy Engine (`backtester/strategies`):** Create a base strategy class that processes signals (like *"If sentiment score > 0.5, BUY"*).
3.  **Backtest Loop (`backtester/engine`):** Write an engine that loops over historical timestamps day-by-day, sends signals to the strategy, and executes trades on the Portfolio.
4.  **Performance Metrics (`backtester/metrics`):** Write formulas to calculate total return, annualized returns, Sharpe Ratio, and maximum drawdown.
