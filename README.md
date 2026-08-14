Stock Analysis & Prediction System

A Python desktop application that fetches historical stock data, engineers technical
indicators, and uses machine learning to forecast future price direction and price
levels. Built as my A-Level Computer Science project.

- Overview

The app is a multi-window Tkinter interface, launched after a simple login/registration
screen, that lets a user:

- Search for any stock ticker and pull its full historical price data (via `yfinance`)
- Choose a prediction horizon from 1 day up to 1 year
- View technical indicators, an interactive price chart, and machine-learning-generated
  price forecasts, all updating live across four separate windows

- Features

- **Login & registration system** — accounts are stored locally with SHA-256 hashed
  passwords (never stored in plaintext), a minimum password length policy, and a
  confirmation step with limited retry attempts.
- **Technical indicator engine** — computes moving averages (5/10/20/50/100/200-day),
  RSI, MACD, Bollinger Bands, volume ratio, price position, Rate of Change, and
  Williams %R from raw OHLCV data.
- **Two prediction approaches**:
  - A **direction classifier** (Gradient Boosting or Random Forest, chosen by horizon
    length) predicting whether price will be up or down at the chosen horizon, with a
    confidence score.
  - A **price regressor** (Gradient Boosting Regression) predicting the actual price
    level, evaluated with RMSE and R².
  - A **MACD-based fallback model** that kicks in when the ML model's confidence is
    low, using the slope of MACD/Signal lines to estimate direction and expected move.
- **Multi-window live interface**, each running in its own thread:
  1. **Control Panel** — search a ticker, pick a prediction horizon, trigger analysis
  2. **Analysis Summary** — final predicted direction/price with confidence
  3. **Interactive Chart** — zoomable price chart with MACD and RSI overlays
  4. **Data & Performance** — historical data table, forecast table, and model
     performance metrics (RMSE, R², training sample size, accuracy)

- Libraries

- **Python 3**
- **Tkinter** — GUI
- **yfinance** — historical stock data
- **pandas / numpy** — data processing
- **scikit-learn** — `GradientBoostingClassifier`, `GradientBoostingRegressor`,
  `RandomForestClassifier`, `LinearRegression`
- **matplotlib** — charting, embedded in Tkinter via `FigureCanvasTkAgg`

- How It Works

1. Historical OHLCV data is pulled for the chosen ticker (as much history as is
   available).
2. A feature set is engineered from that raw data (moving averages, RSI, MACD,
   Bollinger Bands, volume ratio, ROC, Williams %R).
3. Depending on the prediction horizon, the training window is scaled — shorter
   horizons train on the last year of data, while the 1-year horizon uses all
   available history.
4. A classifier is trained to predict up/down direction, and a regressor is trained
   to predict the actual price, both evaluated on a held-out test split.
5. If model confidence is low, the app falls back to a rule-based prediction derived
   from the current slope of the MACD line.
6. Results are displayed across the four windows and refresh automatically.

- Running It

pip install yfinance pandas numpy matplotlib scikit-learn
python CSprototype_07.py

Create an account (or log in), then use the Control Panel window to search a ticker
and run an analysis.


- Disclaimer

This is a learning project built to explore machine learning and financial data
analysis — predictions are not financial advice and should not be used for real
trading decisions.


Author:
Anay Khole
