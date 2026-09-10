# VaRCalc

A Python tool for calculating **Value at Risk (VaR)** and **Conditional Value at Risk (CVaR)** for individual stocks, multi-asset portfolios, and (as of the current phase of work) **options positions**, with an interactive Streamlit dashboard for visual analysis.

VaRCalc pulls historical price data from Yahoo Finance and estimates the potential loss a position could experience over a given time horizon, using three complementary VaR methodologies plus tail-risk analysis.

## Features

- **Multiple VaR methods**
  - **Historical VaR**: empirical percentile of actual past returns
  - **Parametric VaR**: closed-form estimate assuming normally distributed returns
  - **Monte Carlo VaR**: simulation-based estimate (10,000 draws) from a fitted normal distribution
  - **Conditional VaR (CVaR / Expected Shortfall)**: average loss in the tail beyond the VaR threshold
- **Single-stock or portfolio analysis**: analyze one ticker, or a weighted portfolio of up to 10 tickers
- **Diversification insights**: compares portfolio VaR against the weighted average of individual holdings to highlight diversification benefit (or hidden correlation risk)
- **Visualizations**: return distribution histograms with VaR/CVaR overlays, method-comparison bar charts, portfolio-vs-individual risk charts, VaR-vs-CVaR tail-risk charts, rolling VaR/volatility over time, and a combined dashboard view
- **Interactive Streamlit app**: configure tickers, weights, portfolio value, date range, and confidence level, then get a full risk report with plain-English interpretation and recommendations

### Options pricing and Greeks

[`src/options.py`](src/options.py) is a self-contained Black-Scholes-Merton implementation, deliberately decoupled from the VaR engine so the math can be tested and audited independently.

- **Pricing** for European calls and puts, with optional continuous dividend yield
- **Greeks**: delta, gamma, vega, theta, rho, in both raw analytic units and the per-vol-point / per-day conventions brokers quote
- **Implied volatility**: back-solves the market's volatility assumption from an observed option price, using Brent's method so it stays stable for deep in/out-of-the-money and short-dated contracts where vega collapses
- **No-arbitrage validation**: quotes that admit no implied volatility are rejected with a clear diagnostic rather than a solver failure
- **18 unit tests** covering put-call parity, textbook benchmark values, and every Greek verified against central finite differences

## Why options need different treatment

The three VaR methods above all assume a position's P&L is **linear** in the underlying's return: the underlying drops 2%, the position loses 2% of its value. That holds for a stock. It does not hold for an option, whose value is a *curved* function of the underlying price. The curvature is not a rounding error: it dominates for short-dated at-the-money contracts.

Feeding an option's own return history into a linear VaR model treats that curve as a straight line, and the error is worst in the tail, which is the only region VaR actually measures. The next phase of work addresses this by modelling the **underlying's** return distribution and mapping it through a local quadratic approximation of the option's price curve.

## Roadmap

| Phase | Status |
|---|---|
| Core VaR/CVaR engine, three methods, Streamlit dashboard | Complete |
| Migration from yfinance to Polygon.io | In progress |
| Black-Scholes pricing, Greeks, implied volatility | Planned |
| Delta-gamma VaR extension for option positions | Planned |
| Vega / implied-volatility scenario analysis | Planned |

**Delta-gamma VaR** will extend the existing multi-asset framework so that option positions are revalued using a second-order approximation of P&L:

```
ΔP&L ≈ delta × ΔS + ½ × gamma × ΔS²
```

driven by the simulated underlying moves from whichever VaR method is selected. Portfolios mixing options and stocks will produce a blended VaR/CVaR figure that respects convexity. Positions whose gamma is large enough to make the approximation unreliable (very short-dated or far in/out-of-the-money contracts) will be flagged in the output so they can be sanity-checked against a full repricing.

**Vega scenario analysis** will add a direct scenario table showing portfolio value across a range of implied-volatility shocks (−20% through +20%), since volatility exposure is poorly captured by price-based VaR alone.

## Project Structure

```
VaRCalc/
├── gui/
│   ├── app.py              # Streamlit application (main entry point)
│   └── components.py       # (reserved for reusable UI components)
├── src/
│   ├── data_processing.py  # DataProcessor: fetches prices via yfinance, computes returns
│   ├── calculations.py     # Historical, Parametric, Monte Carlo VaR and CVaR
│   ├── visualizations.py   # Matplotlib/Seaborn plotting functions
│   └── utils.py            # (reserved for shared helpers)
├── tests/                  # Unit tests (in progress)
├── docs/                   # Additional documentation (in progress)
├── data/                   # Sample/local data
└── requirements.txt
```

## Getting Started

### Prerequisites

- Python 3.9+
- Internet access (for fetching live price data via Yahoo Finance)

### Installation

```bash
git clone https://github.com/<your-username>/VaRCalc.git
cd VaRCalc

python -m venv venv
source venv/bin/activate      # on Windows: venv\Scripts\activate

pip install -r requirements.txt
```

### API key setup

Market data comes from Polygon.io. The free tier provides end-of-day data at 5 requests per minute, which is sufficient for daily-horizon VaR: one request returns an entire date range per ticker.

1. Create an account at [polygon.io](https://polygon.io/) (no card required for the free tier)
2. From the dashboard, open **API Keys** and copy your key
3. Under **Subscriptions**, confirm the free tiers for both **Stocks** and **Options** are active, since they are granted separately per asset class
4. Create a `.env` file in the project root:

```
POLYGON_API_KEY=your_key_here
```

`.env` is gitignored. Never commit your key: it is a bearer credential.

### Running the App

Launch the Streamlit dashboard from the project root:

```bash
streamlit run gui/app.py
```

Then in the browser UI:

1. Choose **Single Stock** or **Portfolio** analysis
2. Enter ticker symbol(s) (and weights, for a portfolio)
3. Set the total portfolio value, date range, and confidence level
4. Click **Calculate VaR** to view metrics, comparison tables, and visualizations

### Using the Library Directly

The core calculations can also be used without the GUI:

```python
from src.data_processing import DataProcessor
from src.calculations import historical_var, parametric_var, monte_carlo_var, conditional_var

handler = DataProcessor()
prices = handler.fetch_data("AAPL", "2023-01-01", "2024-01-01")
returns = handler.calculate_returns(prices)

hist_var = historical_var(returns, confidence_level=0.95)
param_var = parametric_var(returns, confidence_level=0.95)
mc_var = monte_carlo_var(returns, confidence_level=0.95, num_simulations=10000)
cvar = conditional_var(returns, hist_var)

print(f"Historical VaR (95%): {hist_var:.2%}")
print(f"Conditional VaR (95%): {cvar:.2%}")
```

## Dependencies

- [pandas](https://pandas.pydata.org/) / [numpy](https://numpy.org/): data manipulation
- [scipy](https://scipy.org/): statistical functions and the Brent root-finder used for implied volatility
- [polygon-api-client](https://github.com/polygon-io/client-python): historical market data retrieval
- [python-dotenv](https://github.com/theskumar/python-dotenv): loads the API key from `.env`
- [matplotlib](https://matplotlib.org/) / [seaborn](https://seaborn.pydata.org/): visualizations
- [streamlit](https://streamlit.io/): web app UI

See `requirements.txt` for pinned versions.

## Project Status

This project is under active development. Core VaR/CVaR calculations and visualizations are functional; The API for pulling data has switched from yfinance to Polygon.io (now Massive). The project will also be introducing risk calculations for options, focusing on calculating theoretical value of the option and assessing general risk levels and VaR based on the Greeks generated through the Black-Scholes formula.

## Disclaimer

This tool is intended for **educational purposes** to demonstrate financial risk analysis concepts. It is not investment advice, and past performance/statistical estimates do not guarantee future results.
