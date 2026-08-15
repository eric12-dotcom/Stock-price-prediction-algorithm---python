import json
import os
import hashlib
import tkinter as tk
from tkinter import messagebox, ttk, scrolledtext
from datetime import datetime, timedelta
import threading
import time

# Stock analysis imports
import matplotlib
matplotlib.use('TkAgg')  # Use TkAgg backend so matplotlib renders inside tkinter windows
import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.figure import Figure
import matplotlib.dates as mdates
from sklearn.ensemble import RandomForestClassifier, GradientBoostingRegressor, GradientBoostingClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report, mean_squared_error, r2_score
from sklearn.linear_model import LinearRegression
import warnings
warnings.filterwarnings('ignore')  # Suppress sklearn/pandas deprecation warnings to keep console output clean


# LOGIN SYSTEM


class LoginApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Login & Registration System")

        
        self.root.geometry("400x300")
        self.root.resizable(False, False)
        
        self.users = self.load_users()       # Load any previously registered accounts from disk
        self.password_attempts = 0           # Track failed confirmation attempts during registration
        self.current_password = ""           # Temporarily hold the password between registration steps
        self.password_visible = False        # Toggle state for the registration password field
        self.confirm_visible = False         # Toggle state for the confirmation password field
        self.login_visible = False           # Toggle state for the login password field
        self.current_user = None             # Store the username of whoever is currently logged in
        
        self.setup_main_menu()
        
    def load_users(self):
        # Read the users.txt file if it exists, returning a dict of {username: hashed_password}
        if os.path.exists("users.txt"):
            try:
                with open("users.txt", "r") as f:
                    return json.load(f)
            except:
                return {}
        return {}
    
    def save_users(self):
        # Persist the current users dictionary to users.txt as JSON
        with open("users.txt", "w") as f:
            json.dump(self.users, f)
    
    def hash_password(self, password):
        # Hash the password with SHA-256 so plaintext is never stored or compared directly
        return hashlib.sha256(password.encode()).hexdigest()
    
    def clear_window(self):
        # Destroy all child widgets so the window can be repopulated with a new screen
        for widget in self.root.winfo_children():
            widget.destroy()
    
    def setup_main_menu(self):
        self.clear_window()
        self.root.title("Main Menu")
        self.current_user = None  # Reset logged-in user when returning to the main menu
        
        # Title
        title = tk.Label(self.root, text="Stock Analysis System", 
                        font=("Arial", 16, "bold"), pady=20)
        title.pack()
        
        # Buttons
        btn_frame = tk.Frame(self.root)
        btn_frame.pack(expand=True)
        
        create_btn = tk.Button(btn_frame, text="Create Account", 
                              font=("Arial", 12), width=15, height=2,
                              command=self.setup_registration, bg="#4CAF50", fg="white")
        create_btn.pack(pady=10)
        
        login_btn = tk.Button(btn_frame, text="Login", 
                             font=("Arial", 12), width=15, height=2,
                             command=self.setup_login, bg="#2196F3", fg="white")
        login_btn.pack(pady=10)
        
        exit_btn = tk.Button(btn_frame, text="Exit", 
                            font=("Arial", 12), width=15, height=2,
                            command=self.root.quit, bg="#f44336", fg="white")
        exit_btn.pack(pady=10)
    
    def setup_registration(self):
        self.clear_window()
        self.root.title("Create Account")
        
        # Title
        title = tk.Label(self.root, text="Create Account", 
                        font=("Arial", 16, "bold"), pady=20)
        title.pack()
        
        # Username
        tk.Label(self.root, text="Username:", font=("Arial", 10)).pack()
        self.username_entry = tk.Entry(self.root, font=("Arial", 10), width=25)
        self.username_entry.pack(pady=5)
        
        # Password field with a toggle button to reveal/hide the typed characters
        pass_frame = tk.Frame(self.root)
        pass_frame.pack(pady=5)
        tk.Label(self.root, text="Password (min 12 characters):", font=("Arial", 10)).pack()
        
        pass_input_frame = tk.Frame(self.root)
        pass_input_frame.pack()
        self.password_entry = tk.Entry(pass_input_frame, font=("Arial", 10), width=20, show="*")
        self.password_entry.pack(side=tk.LEFT, padx=2)
        
        self.show_pass_btn = tk.Button(pass_input_frame, text="🔒", width=3,
                                      command=self.toggle_password_visibility)
        self.show_pass_btn.pack(side=tk.LEFT)
        
        # Buttons
        btn_frame = tk.Frame(self.root)
        btn_frame.pack(pady=20)
        
        create_btn = tk.Button(btn_frame, text="Create Account", 
                              font=("Arial", 10), command=self.create_account,
                              bg="#4CAF50", fg="white")
        create_btn.pack(side=tk.LEFT, padx=5)
        
        back_btn = tk.Button(btn_frame, text="Back", 
                            font=("Arial", 10), command=self.setup_main_menu,
                            bg="gray", fg="white")
        back_btn.pack(side=tk.LEFT, padx=5)
    
    def create_account(self):
        username = self.username_entry.get().strip()
        password = self.password_entry.get()
        
        if not username:
            messagebox.showerror("Error", "Username cannot be empty!")
            return
        
        if username in self.users:
            messagebox.showerror("Error", "Username already exists!")
            return
        
        if len(password) < 12:
            # Enforce a minimum password length of 12 characters for security
            messagebox.showerror("Error", "Password must be at least 12 characters long!")
            return
        
        if ' ' in password:
            # Reject passwords containing spaces as they can cause parsing issues
            messagebox.showerror("Error", "Password contains invalid characters!")
            return
        
        # Store password temporarily and reset attempt counter before moving to confirmation step
        self.current_password = password
        self.password_attempts = 0
        self.confirm_visible = False
        self.setup_password_confirmation(username)
    
    def setup_password_confirmation(self, username):
        self.clear_window()
        self.root.title("Confirm Password")
        
        # Title
        title = tk.Label(self.root, text="Confirm Password", 
                        font=("Arial", 16, "bold"), pady=20)
        title.pack()
        
        # Show how many confirmation attempts the user has remaining
        attempts_left = 3 - self.password_attempts
        info = tk.Label(self.root, text=f"Re-enter your password\nAttempts remaining: {attempts_left}", 
                       font=("Arial", 10))
        info.pack(pady=10)
        
        # Confirmation field mirrors the registration field with its own visibility toggle
        tk.Label(self.root, text="Confirm Password:", font=("Arial", 10)).pack()
        confirm_input_frame = tk.Frame(self.root)
        confirm_input_frame.pack()
        self.confirm_entry = tk.Entry(confirm_input_frame, font=("Arial", 10), width=20, show="*")
        self.confirm_entry.pack(side=tk.LEFT, padx=2)
        
        self.show_confirm_btn = tk.Button(confirm_input_frame, text="🔒", width=3,
                                         command=self.toggle_confirm_visibility)
        self.show_confirm_btn.pack(side=tk.LEFT)
        
        # Buttons
        btn_frame = tk.Frame(self.root)
        btn_frame.pack(pady=20)
        
        confirm_btn = tk.Button(btn_frame, text="Confirm", 
                               font=("Arial", 10), 
                               command=lambda: self.confirm_password(username),
                               bg="#4CAF50", fg="white")
        confirm_btn.pack(side=tk.LEFT, padx=5)
        
        back_btn = tk.Button(btn_frame, text="Back", 
                            font=("Arial", 10), command=self.setup_registration,
                            bg="gray", fg="white")
        back_btn.pack(side=tk.LEFT, padx=5)
    
    def confirm_password(self, username):
        confirm_pass = self.confirm_entry.get()
        
        if self.current_password == confirm_pass:
            # Passwords match — hash and save the new account to disk
            hashed_password = self.hash_password(self.current_password)
            self.users[username] = hashed_password
            self.save_users()
            
            # Optionally display the hash so the user can verify how their password is stored
            result = messagebox.askyesno("Account Created", 
                                       "Account created successfully!\n\nWould you like to see your hashed password?")
            if result:
                messagebox.showinfo("Hashed Password", f"Your hashed password:\n{hashed_password}")
            
            messagebox.showinfo("Success", "Redirecting to login page...")
            self.setup_login()
        else:
            self.password_attempts += 1
            if self.password_attempts >= 3:
                # Too many failed attempts — force the user to choose a new password
                messagebox.showerror("Failed", "Too many failed attempts!\nPlease create a new password.")
                self.setup_registration()
            else:
                remaining = 3 - self.password_attempts
                messagebox.showerror("Error", f"Passwords don't match!\n{remaining} attempts remaining.")
                self.setup_password_confirmation(username)
    
    def setup_login(self):
        self.clear_window()
        self.root.title("Login")
        
        # Title
        title = tk.Label(self.root, text="Login", 
                        font=("Arial", 16, "bold"), pady=20)
        title.pack()
        
        # Username
        tk.Label(self.root, text="Username:", font=("Arial", 10)).pack()
        self.login_username = tk.Entry(self.root, font=("Arial", 10), width=25)
        self.login_username.pack(pady=5)
        
        # Password entry with a show/hide toggle for user convenience
        tk.Label(self.root, text="Password:", font=("Arial", 10)).pack()
        login_pass_frame = tk.Frame(self.root)
        login_pass_frame.pack()
        self.login_password = tk.Entry(login_pass_frame, font=("Arial", 10), width=20, show="*")
        self.login_password.pack(side=tk.LEFT, padx=2)
        
        self.show_login_btn = tk.Button(login_pass_frame, text="🔒", width=3,
                                       command=self.toggle_login_visibility)
        self.show_login_btn.pack(side=tk.LEFT)
        
        # Buttons
        btn_frame = tk.Frame(self.root)
        btn_frame.pack(pady=20)
        
        login_btn = tk.Button(btn_frame, text="Login", 
                             font=("Arial", 10), command=self.login,
                             bg="#2196F3", fg="white")
        login_btn.pack(side=tk.LEFT, padx=5)
        
        back_btn = tk.Button(btn_frame, text="Back", 
                            font=("Arial", 10), command=self.setup_main_menu,
                            bg="gray", fg="white")
        back_btn.pack(side=tk.LEFT, padx=5)
        
        # Allow the user to submit the login form by pressing Enter as well as clicking the button
        self.root.bind('<Return>', lambda event: self.login())
        self.login_visible = False
    
    def login(self):
        username = self.login_username.get().strip()
        password = self.login_password.get()
        
        if not username or not password:
            messagebox.showerror("Error", "Please fill in both fields!")
            return
        
        hashed_input = self.hash_password(password)
        
        if username in self.users and self.users[username] == hashed_input:
            # Credentials match — record the logged-in user, close the login window, and launch the app
            self.current_user = username
            messagebox.showinfo("Success", f"Login successful!\n\nWelcome back, {username}!\n\nLaunching Stock Analysis System...")
            self.root.destroy()
            launch_stock_analysis()
        else:
            # Login failed — ask whether to retry or return to the main menu
            result = messagebox.askyesno("Login Failed", 
                                       "Invalid username or password!\n\nWould you like to try again?")
            if result:
                self.login_username.delete(0, tk.END)
                self.login_password.delete(0, tk.END)
                self.login_username.focus()
            else:
                self.setup_main_menu()
    
    def toggle_password_visibility(self):
        # Switch the registration password field between masked and plain-text display
        if self.password_visible:
            self.password_entry.config(show="*")
            self.show_pass_btn.config(text="🔒")
            self.password_visible = False
        else:
            self.password_entry.config(show="")
            self.show_pass_btn.config(text="👁️")
            self.password_visible = True
    
    def toggle_confirm_visibility(self):
        # Switch the confirmation password field between masked and plain-text display
        if self.confirm_visible:
            self.confirm_entry.config(show="*")
            self.show_confirm_btn.config(text="🔒")
            self.confirm_visible = False
        else:
            self.confirm_entry.config(show="")
            self.show_confirm_btn.config(text="👁️")
            self.confirm_visible = True
    
    def toggle_login_visibility(self):
        # Switch the login password field between masked and plain-text display
        if self.login_visible:
            self.login_password.config(show="*")
            self.show_login_btn.config(text="🔒")
            self.login_visible = False
        else:
            self.login_password.config(show="")
            self.show_login_btn.config(text="👁️")
            self.login_visible = True
    
    def run(self):
        self.root.mainloop()


# STOCK ANALYSIS SYSTEM


# Global container that lets all four windows share stock data and analysis results without passing arguments
class SharedStockData:
    def __init__(self):
        self.symbol = 'AAPL'              # Default stock ticker shown on first load
        self.period = 'max'               # Always fetch the maximum available history from yfinance
        self.prediction_horizon = 1       # Number of days ahead to predict (default is next day)
        self.data = None                  # Raw OHLCV DataFrame returned by yfinance
        self.analysis_results = {}        # Processed results dict populated after each analysis run
        self.is_analyzing = False         # Flag used by the UI to show/hide a loading state
        self.training_status = "Ready"    # Human-readable status message updated during analysis
        self.progress_value = 0           # Integer 0–100 driving the progress bar in the control panel
        
shared_data = SharedStockData()

class StockAnalyzer:
    def __init__(self):
        # Map display labels to their corresponding number of calendar days for the dropdown
        self.prediction_options = {
            '1 Day': 1,
            '1 Week': 7,
            '2 Weeks': 14,
            '1 Month': 30,
            '2 Months': 60,
            '3 Months': 90,
            '6 Months': 180,
            '1 Year': 365
        }
        
        # Longer prediction horizons use more historical data so the model can learn slower trends
        self.training_windows = {
            1: 365,
            7: 365,
            14: 547,
            30: 730,
            60: 1095,
            90: 1460,
            180: 1825,
            365: None   # None means use all available data for the 1-year horizon
        }
    
    def get_training_window(self, horizon_days):
        # Return the appropriate training window size in days for the given prediction horizon
        return self.training_windows.get(horizon_days, 730)
    
    def fetch_data(self, symbol):
        try:
            shared_data.progress_value = 5
            shared_data.training_status = f"Fetching maximum data for {symbol}..."
            stock = yf.Ticker(symbol)
            
            # Try to download the full price history; fall back to shorter periods if "max" fails
            data = stock.history(period="max")
            
            if data.empty:
                for period in ["10y", "5y", "2y", "1y"]:
                    try:
                        data = stock.history(period=period)
                        if not data.empty:
                            break
                    except:
                        continue
            
            if not data.empty:
                start_date = data.index[0].strftime('%Y-%m-%d')
                end_date = data.index[-1].strftime('%Y-%m-%d')
                years_of_data = (data.index[-1] - data.index[0]).days / 365.25
                shared_data.training_status = f"Loaded {len(data)} days ({years_of_data:.1f} years) from {start_date} to {end_date}"
                shared_data.progress_value = 15
                time.sleep(0.5)
            
            return data
        except Exception as e:
            shared_data.training_status = f"Error fetching data: {str(e)}"
            shared_data.progress_value = 0
            return None
    
    def create_features(self, data):
        df = data.copy()
        
        shared_data.training_status = "Creating technical indicators..."
        shared_data.progress_value = 20
        
        # Cap rolling window at 200 or a quarter of the dataset to avoid NaN-heavy short histories
        max_period = min(200, len(df) // 4)
        
        # Moving averages over several timeframes capture short, medium and long-term price trends
        df['MA_5'] = df['Close'].rolling(min(5, max_period // 40)).mean()
        df['MA_10'] = df['Close'].rolling(min(10, max_period // 20)).mean()
        df['MA_20'] = df['Close'].rolling(min(20, max_period // 10)).mean()
        df['MA_50'] = df['Close'].rolling(min(50, max_period // 4)).mean()
        df['MA_100'] = df['Close'].rolling(min(100, max_period // 2)).mean()
        df['MA_200'] = df['Close'].rolling(min(200, max_period)).mean()
        
        # RSI measures momentum by comparing average gains to average losses over 14 periods
        delta = df['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
        rs = gain / loss
        df['RSI'] = 100 - (100 / (1 + rs))
        
        # MACD highlights trend direction and momentum by comparing two exponential moving averages
        exp1 = df['Close'].ewm(span=12).mean()
        exp2 = df['Close'].ewm(span=26).mean()
        df['MACD'] = exp1 - exp2
        df['MACD_Signal'] = df['MACD'].ewm(span=9).mean()
        df['MACD_Histogram'] = df['MACD'] - df['MACD_Signal']  # Positive histogram means bullish momentum
        
        # Bollinger Bands show price volatility and where the price sits relative to recent range
        df['BB_Middle'] = df['Close'].rolling(20).mean()
        bb_std = df['Close'].rolling(20).std()
        df['BB_Upper'] = df['BB_Middle'] + (bb_std * 2)
        df['BB_Lower'] = df['BB_Middle'] - (bb_std * 2)
        df['BB_Width'] = df['BB_Upper'] - df['BB_Lower']
        df['BB_Position'] = (df['Close'] - df['BB_Lower']) / (df['BB_Upper'] - df['BB_Lower'])
        
        # Volume indicators help detect whether price moves are backed by trading activity
        df['Volume_MA'] = df['Volume'].rolling(20).mean()
        df['Volume_Ratio'] = df['Volume'] / df['Volume_MA']
        df['Price_Change_Pct'] = df['Close'].pct_change() * 100
        
        # Rolling standard deviation of Close price as a simple measure of recent volatility
        df['Volatility'] = df['Close'].rolling(20).std()
        
        # Normalised position of today's close within the 20-day high/low range (0 = at low, 1 = at high)
        df['Price_Position'] = (df['Close'] - df['Low'].rolling(20).min()) / (df['High'].rolling(20).max() - df['Low'].rolling(20).min())
        
        # ROC and Williams %R provide additional momentum context for the ML models
        df['ROC'] = ((df['Close'] - df['Close'].shift(12)) / df['Close'].shift(12)) * 100
        df['Williams_R'] = ((df['High'].rolling(14).max() - df['Close']) / (df['High'].rolling(14).max() - df['Low'].rolling(14).min())) * -100
        
        shared_data.progress_value = 30
        return df
    
    def predict_macd_trend(self, data, horizon_days):
        """Enhanced MACD-based trend prediction with confidence scoring"""
        df = self.create_features(data)
        
        # Use only the most recent 30 days so the linear fit reflects current momentum, not historical noise
        recent_macd = df[['MACD', 'MACD_Signal', 'MACD_Histogram', 'Close']].tail(30).dropna()
        
        if len(recent_macd) < 20:
            return None
        
        # Fit linear regression lines to MACD and Signal to estimate their current slopes
        X = np.arange(len(recent_macd)).reshape(-1, 1)
        
        macd_model = LinearRegression()
        macd_model.fit(X, recent_macd['MACD'].values)
        
        signal_model = LinearRegression()
        signal_model.fit(X, recent_macd['MACD_Signal'].values)
        
        # Snapshot of current indicator values used to classify the signal
        current_macd = recent_macd['MACD'].iloc[-1]
        current_signal = recent_macd['MACD_Signal'].iloc[-1]
        current_histogram = recent_macd['MACD_Histogram'].iloc[-1]
        current_price = recent_macd['Close'].iloc[-1]
        
        # Slopes tell us whether each line is rising or falling right now
        macd_slope = macd_model.coef_[0]
        signal_slope = signal_model.coef_[0]
        histogram_slope = macd_slope - signal_slope  # Positive means the gap between MACD and Signal is widening
        
        # Scale momentum strength from the slope magnitude for use in confidence scoring
        momentum_score = abs(macd_slope) * 100
        
        
        # Decision logic — classify the signal as bullish, bearish, or neutral and assign confidence
        is_bullish = False
        is_bearish = False
        confidence = 0

        # Strong bullish: MACD above Signal and both lines rising with widening histogram
        if current_macd > current_signal and macd_slope > 0 and histogram_slope > 0:
            is_bullish = True
            confidence = min(95, 70 + momentum_score * 5)
        # Moderate bullish: MACD above Signal but momentum may be slowing
        elif current_macd > current_signal:
            if current_histogram > 0:  # Histogram still positive — trend intact even if decelerating
                is_bullish = True
                confidence = min(75, 60 + momentum_score * 3)
            else:  # Histogram turned negative — weakening bullish, treat as neutral
                confidence = 50
        # Strong bearish: MACD below Signal and both lines falling with widening negative histogram
        elif current_macd < current_signal and macd_slope < 0 and histogram_slope < 0:
            is_bearish = True
            confidence = min(95, 70 + momentum_score * 5)
        # Moderate bearish: MACD below Signal but histogram may be recovering
        elif current_macd < current_signal:
            if current_histogram < 0:  # Still bearish even if the sell-off is slowing
                is_bearish = True
                confidence = min(75, 60 + momentum_score * 3)
            else:  # Histogram recovering — weakening bearish, treat as neutral
                confidence = 50
        # Neither condition met — genuinely neutral/undecided signal
        else:
            confidence = 40      
        
        # Estimate the expected price move using recent volatility scaled by confidence and horizon
        recent_volatility = recent_macd['Close'].pct_change().std()
        price_change_factor = recent_volatility * (confidence / 100) * horizon_days * 0.1

        if is_bullish:
            predicted_price = current_price * (1 + price_change_factor)
            direction = "📈 UP"
        elif is_bearish:
            predicted_price = current_price * (1 - price_change_factor)
            direction = "📉 DOWN"
        else:
            # Neutral: apply a small positive drift rather than zero change
            predicted_price = current_price * (1 + price_change_factor * 0.3)
            direction = "🟡 NEUTRAL"
            confidence = 40

        # Sanity check: ensure the direction label matches the sign of the predicted price change
        price_change = predicted_price - current_price
        if price_change > 0 and direction == "📉 DOWN":
            direction = "📈 UP"  # Correct label mismatch
        elif price_change < 0 and direction == "📈 UP":
            direction = "📉 DOWN"  # Correct label mismatch
        
        # Guard against a meaningless prediction where the price lands exactly on the current value
        if abs(predicted_price - current_price) < 0.01:
            if direction == "📈 UP":
                predicted_price = current_price * 1.001
            elif direction == "📉 DOWN":
                predicted_price = current_price * 0.999
            else:
                predicted_price = current_price * 1.0005
        
        return {
            'direction': direction,
            'confidence': confidence,
            'predicted_price': predicted_price,
            'current_price': current_price,
            'price_change': predicted_price - current_price,
            'price_change_pct': ((predicted_price - current_price) / current_price) * 100,
            'momentum_score': momentum_score,
            'macd_slope': macd_slope,
            'signal_slope': signal_slope,
            'histogram_trend': "Increasing" if current_histogram > recent_macd['MACD_Histogram'].iloc[-5] else "Decreasing",
            'is_macd_falling': macd_slope < 0  # True when MACD line itself is declining, signalling bearish pressure
        }
    
    def analyze_trend(self, data, days=20):
        df = self.create_features(data)
        recent_data = df.tail(days)
        
        # Determine overall price direction by comparing the last close to the close 20 days ago
        price_trend = "📈 UPWARD" if recent_data['Close'].iloc[-1] > recent_data['Close'].iloc[0] else "📉 DOWNWARD"
        trend_strength = abs(((recent_data['Close'].iloc[-1] / recent_data['Close'].iloc[0]) - 1) * 100)
        
        current_price = recent_data['Close'].iloc[-1]
        ma_5 = recent_data['MA_5'].iloc[-1]
        ma_20 = recent_data['MA_20'].iloc[-1]
        
        # Classic MA alignment check: price > MA5 > MA20 signals a bullish stack
        if current_price > ma_5 > ma_20:
            ma_signal = "🟢 BULLISH"
        elif current_price < ma_5 < ma_20:
            ma_signal = "🔴 BEARISH"
        else:
            ma_signal = "🟡 MIXED"
        
        # RSI thresholds: above 70 is traditionally overbought, below 30 is oversold
        current_rsi = recent_data['RSI'].iloc[-1]
        if current_rsi > 70:
            rsi_signal = f"⚠️ OVERBOUGHT ({current_rsi:.1f})"
        elif current_rsi < 30:
            rsi_signal = f"💰 OVERSOLD ({current_rsi:.1f})"
        else:
            rsi_signal = f"⚖️ NEUTRAL ({current_rsi:.1f})"
        
        return {
            'trend': price_trend,
            'strength': trend_strength,
            'ma_signal': ma_signal,
            'rsi_signal': rsi_signal,
            'current_price': current_price,
            'data_years': (data.index[-1] - data.index[0]).days / 365.25,
            'total_days': len(data)
        }
    
    def predict_direction(self, data, horizon_days):
        shared_data.training_status = f"Training direction model for {horizon_days} days..."
        shared_data.progress_value = 40
        
        training_window = self.get_training_window(horizon_days)
        
        # Slice to the relevant training window so shorter horizons aren't crowded by ancient data
        if training_window and len(data) > training_window:
            data_windowed = data.tail(training_window)
            window_years = training_window / 365.25
            shared_data.training_status = f"Using last {window_years:.1f} years of data for training..."
        else:
            data_windowed = data
            shared_data.training_status = f"Using all available data for training..."
        
        df = self.create_features(data_windowed)
        
        features = ['Open', 'High', 'Low', 'Volume', 'MA_5', 'MA_10', 'MA_20', 'MA_50', 'MA_100', 'MA_200',
                   'RSI', 'MACD', 'MACD_Signal', 'MACD_Histogram', 'BB_Position', 'Volume_Ratio',
                   'Price_Position', 'ROC', 'Williams_R']
        
        # Only include features that were actually created (some may be missing on very short datasets)
        available_features = [f for f in features if f in df.columns]
        
        # Binary target: 1 if the price is higher horizon_days later, 0 if lower
        df['Target'] = (df['Close'].shift(-horizon_days) > df['Close']).astype(int)
        df_clean = df.dropna()
        
        if len(df_clean) < 100:
            return {'direction': "❓ INSUFFICIENT DATA", 'confidence': 0, 'model_accuracy': 0, 
                    'training_samples': len(df_clean), 'training_years': 0}
        
        X = df_clean[available_features]
        y = df_clean['Target']
        
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        
        # Use Gradient Boosting for short horizons (higher precision) and Random Forest for longer ones (better generalisation)
        if horizon_days <= 7:
            model = GradientBoostingClassifier(n_estimators=250, learning_rate=0.12, max_depth=7, random_state=42)
        elif horizon_days <= 30:
            model = GradientBoostingClassifier(n_estimators=200, learning_rate=0.1, max_depth=6, random_state=42)
        else:
            model = RandomForestClassifier(n_estimators=250, max_depth=10, random_state=42)
        
        shared_data.training_status = f"Training on {len(X_train)} samples..."
        shared_data.progress_value = 50
        model.fit(X_train, y_train)
        
        y_pred = model.predict(X_test)
        accuracy = accuracy_score(y_test, y_pred)
        
        # Predict on the most recent available feature row to get the forward-looking signal
        latest_features = X.iloc[-1:].values
        next_direction = model.predict(latest_features)[0]
        confidence = model.predict_proba(latest_features)[0].max()
        
        direction_text = "📈 UP" if next_direction == 1 else "📉 DOWN"
        
        training_years = len(data_windowed) / 365.25
        
        return {
            'direction': direction_text,
            'confidence': confidence * 100,
            'model_accuracy': accuracy * 100,
            'training_samples': len(X_train),
            'training_years': training_years
        }
    
    def predict_exact_price(self, data, horizon_days):
        shared_data.training_status = f"Training price prediction model for {horizon_days} days..."
        shared_data.progress_value = 60
        
        training_window = self.get_training_window(horizon_days)
        
        # Apply the same windowing logic as the direction model for consistency
        if training_window and len(data) > training_window:
            data_windowed = data.tail(training_window)
        else:
            data_windowed = data
        
        df = self.create_features(data_windowed)
        
        features = ['Open', 'High', 'Low', 'Volume', 'MA_5', 'MA_10', 'MA_20', 'MA_50', 'MA_100', 'MA_200',
                   'RSI', 'MACD', 'MACD_Signal', 'MACD_Histogram', 'BB_Position', 'Volume_Ratio',
                   'Price_Position', 'ROC', 'Williams_R']
        
        available_features = [f for f in features if f in df.columns]
        
        # Regression target: the actual closing price horizon_days into the future
        df['Target_Price'] = df['Close'].shift(-horizon_days)
        df_clean = df.dropna()
        
        if len(df_clean) < 100:
            # Not enough data to train — return a minimal placeholder prediction rather than crashing
            current_price = df['Close'].iloc[-1]
            return {
                'predicted_price': current_price * 1.001,  # Force small change
                'current_price': current_price,
                'price_change': current_price * 0.001,
                'price_change_pct': 0.1,
                'model_rmse': 0,
                'model_r2': 0,
                'prediction_date': (datetime.now() + timedelta(days=horizon_days)).strftime('%Y-%m-%d'),
                'training_samples': len(df_clean),
                'training_years': 0
            }
        
        X = df_clean[available_features]
        y = df_clean['Target_Price']
        
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        
        # Gradient Boosting regressor with parameters tuned per horizon: tighter learning rate for longer forecasts
        if horizon_days <= 7:
            model = GradientBoostingRegressor(n_estimators=250, learning_rate=0.12, max_depth=7, random_state=42)
        elif horizon_days <= 30:
            model = GradientBoostingRegressor(n_estimators=200, learning_rate=0.1, max_depth=6, random_state=42)
        else:
            model = GradientBoostingRegressor(n_estimators=150, learning_rate=0.08, max_depth=5, random_state=42)
        
        shared_data.training_status = f"Training on {len(X_train)} samples..."
        shared_data.progress_value = 75
        model.fit(X_train, y_train)
        
        y_pred = model.predict(X_test)
        mse = mean_squared_error(y_test, y_pred)
        rmse = np.sqrt(mse)
        r2 = r2_score(y_test, y_pred)
        
        latest_features = X.iloc[-1:].values
        predicted_price = model.predict(latest_features)[0]
        current_price = df['Close'].iloc[-1]
        
        # If the model predicts virtually no change, nudge the price by a volatility-scaled amount
        if abs(predicted_price - current_price) < 0.01:
            recent_volatility = df['Close'].tail(20).std()
            random_change = np.random.choice([-1, 1]) * max(0.01, recent_volatility * 0.1)
            predicted_price = current_price + random_change
        
        price_change = predicted_price - current_price
        price_change_pct = (price_change / current_price) * 100
        
        prediction_date = (datetime.now() + timedelta(days=horizon_days)).strftime('%Y-%m-%d')
        
        training_years = len(data_windowed) / 365.25
        
        return {
            'predicted_price': predicted_price,
            'current_price': current_price,
            'price_change': price_change,
            'price_change_pct': price_change_pct,
            'model_rmse': rmse,
            'model_r2': r2,
            'prediction_date': prediction_date,
            'training_samples': len(X_train),
            'training_years': training_years
        }
    
    def generate_price_forecast(self, data, horizon_days):
        """Generate multiple price points for charting"""
        shared_data.training_status = "Generating forecast points..."
        shared_data.progress_value = 80
        
        df = self.create_features(data)
        forecast_points = []
        
        # Build a set of intermediate prediction dates appropriate to the total horizon length
        if horizon_days <= 7:
            prediction_intervals = list(range(1, horizon_days + 1))
        elif horizon_days <= 30:
            prediction_intervals = [1, 3, 7, 14, 21] + ([horizon_days] if horizon_days not in [1, 3, 7, 14, 21] else [])
        elif horizon_days <= 90:
            prediction_intervals = [1, 7, 14, 30, 60] + ([horizon_days] if horizon_days not in [1, 7, 14, 30, 60] else [])
        elif horizon_days <= 180:
            prediction_intervals = [1, 7, 30, 60, 90, 120, 150] + ([horizon_days] if horizon_days not in [1, 7, 30, 60, 90, 120, 150] else [])
        else:
            prediction_intervals = [1, 7, 30, 60, 90, 120, 180, 240, 300] + ([horizon_days] if horizon_days not in [1, 7, 30, 60, 90, 120, 180, 240, 300] else [])
        
        # Deduplicate and sort, capping at the selected horizon so we never predict beyond the target date
        prediction_intervals = sorted(list(set([x for x in prediction_intervals if x <= horizon_days])))
        
        total_predictions = len(prediction_intervals)
        for i, days in enumerate(prediction_intervals):
            # Update progress bar incrementally as each intermediate prediction is generated
            progress = 80 + (15 * (i / total_predictions))
            shared_data.progress_value = int(progress)
            shared_data.training_status = f"Generating prediction {i+1}/{total_predictions} ({days} days)..."
            
            try:
                price_pred = self.predict_exact_price(data, days)
                if price_pred['training_samples'] >= 50:
                    forecast_points.append({
                        'days': days,
                        'date': (datetime.now() + timedelta(days=days)).strftime('%Y-%m-%d'),
                        'predicted_price': price_pred['predicted_price']
                    })
            except Exception as e:
                print(f"Error predicting for {days} days: {e}")
                continue
        
        shared_data.progress_value = 95
        return forecast_points

analyzer = StockAnalyzer()

def run_stock_analysis():
    # Entry point for the background analysis thread — sets the busy flag and resets progress
    shared_data.is_analyzing = True
    shared_data.progress_value = 0
    shared_data.training_status = "Starting analysis..."
    
    try:
        data = analyzer.fetch_data(shared_data.symbol)
        if data is not None:
            shared_data.data = data
            
            shared_data.training_status = "Training models..."
            
            trend_analysis = analyzer.analyze_trend(data)
            direction_pred = analyzer.predict_direction(data, shared_data.prediction_horizon)
            price_pred = analyzer.predict_exact_price(data, shared_data.prediction_horizon)

            # MACD trend is always computed so it can appear in the summary even when not used as the main signal
            shared_data.training_status = "Analyzing MACD trend..."
            macd_trend = analyzer.predict_macd_trend(data, shared_data.prediction_horizon)

            # Start with the ML price prediction as the default, then potentially override with MACD
            final_prediction = price_pred.copy()
            prediction_source = "ML Model"

            # Keep the direction label consistent with the sign of the price change
            if final_prediction['price_change'] > 0:
                direction_pred['direction'] = "📈 UP"
            elif final_prediction['price_change'] < 0:
                direction_pred['direction'] = "📉 DOWN"
            else:
                direction_pred['direction'] = "🟡 NEUTRAL"
            
            # For 1-day or 1-week horizons, switch to the MACD signal if the ML model looks unreliable
            if shared_data.prediction_horizon <= 7:
                if macd_trend and (price_pred['model_r2'] < 0.6 or direction_pred['confidence'] < 65):
                    final_prediction['predicted_price'] = macd_trend['predicted_price']
                    final_prediction['price_change'] = macd_trend['price_change']
                    final_prediction['price_change_pct'] = macd_trend['price_change_pct']
                    direction_pred['direction'] = macd_trend['direction']
                    direction_pred['confidence'] = macd_trend['confidence']
                    prediction_source = "MACD Trend"
            
            shared_data.training_status = "Generating forecast points..."
            forecast = analyzer.generate_price_forecast(data, shared_data.prediction_horizon)
            
            # Bundle all results into shared_data so every window can read them on its next refresh
            shared_data.analysis_results = {
                'trend': trend_analysis,
                'direction': direction_pred,
                'price': final_prediction,
                'macd_trend': macd_trend,
                'forecast': forecast,
                'horizon_days': shared_data.prediction_horizon,
                'timestamp': datetime.now().strftime('%H:%M:%S'),
                'prediction_source': prediction_source
            }
            
            shared_data.training_status = f"Complete! Prediction from {prediction_source}"
            shared_data.progress_value = 100
            
    except Exception as e:
        shared_data.training_status = f"Analysis error: {str(e)}"
        shared_data.progress_value = 0
        print(f"Analysis error: {e}")
    finally:
        shared_data.is_analyzing = False  # Always clear the busy flag so the UI doesn't get stuck in a loading state

def create_control_window(window_id, x_pos, y_pos, color, content_config):
    """Control panel window for stock selection"""
    root = tk.Tk()
    root.title("Stock Analysis Control Panel")
    root.geometry(f"400x700+{x_pos}+{y_pos}")
    root.configure(bg=color)
    
    title_label = tk.Label(root, text="🎛️ Stock Analysis Control", 
                          font=("Arial", 16, "bold"), bg=color, fg="white")
    title_label.pack(pady=10)
    
    search_frame = tk.LabelFrame(root, text="Search Stock", bg=color, fg="white", font=("Arial", 12))
    search_frame.pack(pady=10, padx=20, fill="x")
    
    search_var = tk.StringVar(value=shared_data.symbol)
    search_entry = tk.Entry(search_frame, textvariable=search_var, font=("Arial", 12))
    search_entry.pack(pady=10, padx=10, fill="x")
    
    def on_search():
        # Push the typed ticker into shared_data so all windows pick up the new symbol
        symbol = search_var.get().strip().upper()
        if symbol:
            shared_data.symbol = symbol
            stock_var.set(symbol)
    
    search_btn = tk.Button(search_frame, text="🔍 Search Stock", command=on_search,
                          font=("Arial", 11, "bold"), bg="#2196F3", fg="white")
    search_btn.pack(pady=(0, 10), padx=10, fill="x")
    
    stock_frame = tk.LabelFrame(root, text="Current Stock", bg=color, fg="white", font=("Arial", 12))
    stock_frame.pack(pady=10, padx=20, fill="x")
    
    stock_var = tk.StringVar(value=shared_data.symbol)
    stock_label = tk.Label(stock_frame, textvariable=stock_var, font=("Arial", 14, "bold"),
                          bg=color, fg="cyan")
    stock_label.pack(pady=10, padx=10)
    
    info_label = tk.Label(stock_frame, text="📊 Enhanced with MACD fallback logic", 
                         font=("Arial", 9), bg=color, fg="lightgray")
    info_label.pack(pady=5)
    
    horizon_frame = tk.LabelFrame(root, text="Prediction Horizon", bg=color, fg="white", font=("Arial", 12))
    horizon_frame.pack(pady=10, padx=20, fill="x")
    
    horizon_var = tk.StringVar(value="1 Day")
    horizon_combo = ttk.Combobox(horizon_frame, textvariable=horizon_var,
                                values=list(analyzer.prediction_options.keys()), state="readonly")
    horizon_combo.pack(pady=10, padx=10, fill="x")
    
    horizon_info = tk.Label(horizon_frame, text="Uses MACD for short-term if ML confidence low", 
                           font=("Arial", 9), bg=color, fg="lightgray")
    horizon_info.pack(pady=5)
    
    progress_frame = tk.Frame(root, bg=color)
    progress_frame.pack(pady=10, padx=20, fill="x")
    
    progress_bar = ttk.Progressbar(progress_frame, length=350, mode='determinate', maximum=100)
    progress_bar.pack(pady=5)
    
    training_var = tk.StringVar(value="Ready")
    training_label = tk.Label(root, textvariable=training_var, font=("Arial", 10), 
                             bg=color, fg="cyan", wraplength=350)
    training_label.pack(pady=5)
    
    status_var = tk.StringVar(value="Ready")
    status_label = tk.Label(root, textvariable=status_var, font=("Arial", 11, "bold"), 
                           bg=color, fg="yellow")
    status_label.pack(pady=10)
    
    def on_analyze():
        # Copy current UI selections into shared_data before spawning the analysis thread
        shared_data.symbol = stock_var.get()
        shared_data.prediction_horizon = analyzer.prediction_options[horizon_var.get()]
        status_var.set("Analyzing...")
        progress_bar['value'] = 0
        
        analysis_thread = threading.Thread(target=run_stock_analysis, daemon=True)
        analysis_thread.start()
    
    analyze_btn = tk.Button(root, text="🔍 Analyze Stock", command=on_analyze,
                           font=("Arial", 14, "bold"), bg="lightgreen", fg="black")
    analyze_btn.pack(pady=20)
    
    def update_status():
        # Poll shared_data every 100 ms so the progress bar and status text stay in sync with the thread
        training_var.set(shared_data.training_status)
        stock_var.set(shared_data.symbol)
        progress_bar['value'] = shared_data.progress_value
        
        if shared_data.is_analyzing:
            status_var.set(f"Analyzing... {shared_data.progress_value}%")
        elif shared_data.analysis_results:
            status_var.set(f"✓ Complete - {shared_data.analysis_results.get('timestamp', 'Unknown')}")
        else:
            status_var.set("Ready")
        root.after(100, update_status)
    
    update_status()
    
    selection_frame = tk.LabelFrame(root, text="Current Selection", bg=color, fg="white")
    selection_frame.pack(pady=10, padx=20, fill="both", expand=True)
    
    selection_text = tk.Text(selection_frame, height=8, wrap=tk.WORD, font=("Arial", 10))
    selection_text.pack(pady=10, padx=10, fill="both", expand=True)
    
    def update_selection_display():
        # Rebuild the summary text box every 2 seconds with the latest shared_data values
        selection_text.delete(1.0, tk.END)
        info = f"Stock: {shared_data.symbol}\n"
        info += f"Horizon: {shared_data.prediction_horizon} days\n\n"
        
        training_window = analyzer.get_training_window(shared_data.prediction_horizon)
        if training_window:
            info += f"Training Window: {training_window/365.25:.1f} years\n"
        else:
            info += f"Training Window: All available data\n"
        
        if shared_data.analysis_results:
            trend = shared_data.analysis_results['trend']
            price = shared_data.analysis_results['price']
            source = shared_data.analysis_results.get('prediction_source', 'ML Model')
            info += f"\nSource: {source}\n"
            info += f"Full Data: {trend['data_years']:.1f} years\n"
            info += f"Current Price: ${trend['current_price']:.2f}\n"
            info += f"Predicted: ${price['predicted_price']:.2f}\n"
            info += f"Change: {price['price_change_pct']:+.2f}%\n"
            info += f"Target: {price['prediction_date']}\n"
        
        selection_text.insert(1.0, info)
        root.after(2000, update_selection_display)
    
    update_selection_display()
    
    root.mainloop()

def create_summary_window(window_id, x_pos, y_pos, color, content_config):
    """Summary and predictions window"""
    root = tk.Tk()
    root.title("Stock Analysis Summary")
    root.geometry(f"500x750+{x_pos}+{y_pos}")
    root.configure(bg=color)
    
    title_label = tk.Label(root, text="📊 Analysis Summary", 
                          font=("Arial", 16, "bold"), bg=color, fg="white")
    title_label.pack(pady=10)
    
    summary_frame = tk.LabelFrame(root, text="Predictions & Analysis", bg=color, fg="white")
    summary_frame.pack(pady=10, padx=20, fill="both", expand=True)
    
    # Dark-themed scrolled text area styled to look like a terminal readout
    summary_text = scrolledtext.ScrolledText(summary_frame, height=35, wrap=tk.WORD, 
                                           font=("Courier", 9), bg="black", fg="lime")
    summary_text.pack(pady=10, padx=10, fill="both", expand=True)
    
    def update_summary():
        summary_text.delete(1.0, tk.END)
        
        if not shared_data.analysis_results:
            summary_text.insert(tk.END, "No analysis data available.\nPlease run analysis from Control Panel.")
            root.after(2000, update_summary)
            return
        
        results = shared_data.analysis_results
        trend = results['trend']
        direction = results['direction']
        price = results['price']
        macd_trend = results.get('macd_trend')
        horizon_days = results.get('horizon_days', 1)
        prediction_source = results.get('prediction_source', 'ML Model')
        
        # Convert the raw horizon integer to a human-readable label for the report header
        if horizon_days == 1:
            horizon_desc = "1 Day"
        elif horizon_days == 7:
            horizon_desc = "1 Week"
        elif horizon_days == 14:
            horizon_desc = "2 Weeks"
        elif horizon_days == 30:
            horizon_desc = "1 Month"
        elif horizon_days == 60:
            horizon_desc = "2 Months"
        elif horizon_days == 90:
            horizon_desc = "3 Months"
        elif horizon_days == 180:
            horizon_desc = "6 Months"
        elif horizon_days == 365:
            horizon_desc = "1 Year"
        else:
            horizon_desc = f"{horizon_days} Days"
        
        summary = f"""
╔════════════════════════════════════════════╗
║           STOCK ANALYSIS REPORT            ║
╚════════════════════════════════════════════╝

STOCK: {shared_data.symbol}
FULL DATA: {trend['data_years']:.1f} years ({trend['total_days']} days)
TRAINING DATA: {price['training_years']:.1f} years
PREDICTION HORIZON: {horizon_desc}
PREDICTION SOURCE: {prediction_source}
UPDATED: {results['timestamp']}

┌─ CURRENT STATUS ─────────────────────────────┐
│ Price: ${trend['current_price']:.2f}
│ Trend: {trend['trend']}
│ Strength: {trend['strength']:.1f}%
│ MA Signal: {trend['ma_signal']}
│ RSI: {trend['rsi_signal']}
└──────────────────────────────────────────────┘

┌─ FINAL PREDICTION ({horizon_desc}) ────────────────┐
│ Direction: {direction['direction']}
│ Confidence: {direction['confidence']:.1f}%
│
│ Target Date: {price['prediction_date']}
│ Target Price: ${price['predicted_price']:.2f}
│ Expected Change: ${price['price_change']:+.2f}
│ Change %: {price['price_change_pct']:+.2f}%
│
│ Source: {prediction_source}
└──────────────────────────────────────────────┘
"""
        
        if macd_trend:
            # Show whether MACD is the active prediction source or just an additional reference signal
            macd_status = "✓ ACTIVE" if prediction_source == "MACD Trend" else "Available"
            summary += f"""
┌─ MACD TREND ANALYSIS ({macd_status}) ────────────┐
│ Direction: {macd_trend['direction']}
│ Confidence: {macd_trend['confidence']:.1f}%
│ MACD Falling: {"YES ⚠️" if macd_trend['is_macd_falling'] else "NO"}
│
│ MACD Price Target: ${macd_trend['predicted_price']:.2f}
│ MACD Change: {macd_trend['price_change_pct']:+.2f}%
│
│ MACD Slope: {macd_trend['macd_slope']:.4f}
│ Signal Slope: {macd_trend['signal_slope']:.4f}
│ Histogram: {macd_trend['histogram_trend']}
└──────────────────────────────────────────────┘
"""
        
        if 'forecast' in results and results['forecast']:
            summary += "\n┌─ INTERMEDIATE PREDICTIONS ───────────────────┐\n"
            for point in results['forecast'][:8]:
                summary += f"│ {point['date']}: ${point['predicted_price']:.2f}\n"
            if len(results['forecast']) > 8:
                summary += f"│ ... and {len(results['forecast']) - 8} more points\n"
            summary += "└──────────────────────────────────────────────┘\n"
        
        summary += f"""
┌─ RECOMMENDATION ─────────────────────────────┐
│ Based on {horizon_desc} analysis:
"""
        
        # Thresholds scale with horizon: shorter predictions require higher confidence to act on
        confidence_threshold = 70 if horizon_days <= 7 else 65 if horizon_days <= 30 else 60
        price_threshold = 1.5 if horizon_days <= 7 else 2 if horizon_days <= 30 else 3
        
        if direction['confidence'] > confidence_threshold and price['price_change_pct'] > price_threshold:
            summary += "│ 🟢 STRONG BUY signal\n"
        elif direction['confidence'] > (confidence_threshold - 10) and price['price_change_pct'] > 0:
            summary += "│ 🟡 MODERATE BUY signal\n"
        elif direction['confidence'] > (confidence_threshold - 10) and price['price_change_pct'] < -price_threshold:
            summary += "│ 🔴 STRONG SELL signal\n"
        elif price['price_change_pct'] < 0:
            summary += "│ 🟠 SELL signal\n"
        else:
            summary += "│ ⚪ HOLD - Minimal movement expected\n"
        
        # Falling MACD on a short-term prediction is an additional bearish warning worth flagging explicitly
        if macd_trend and macd_trend['is_macd_falling'] and horizon_days <= 7:
            summary += "│ ⚠️  MACD is falling - Bearish pressure\n"
        
        summary += f"│ Prediction Method: {prediction_source}\n"
        
        summary += "│ \n│ ⚠️  Always validate with multiple sources.\n"
        summary += "└──────────────────────────────────────────────┘\n"
        
        summary_text.insert(tk.END, summary)
        root.after(5000, update_summary)  # Refresh the summary every 5 seconds to catch new analysis results
    
    update_summary()
    root.mainloop()

def create_chart_window(window_id, x_pos, y_pos, color, content_config):
    """Interactive price chart window with zoom toolbar at TOP"""
    root = tk.Tk()
    root.title("Interactive Stock Price Chart - ZOOM ENABLED")
    root.geometry(f"1200x900+{x_pos}+{y_pos}")
    root.configure(bg=color)
    
    # Toolbar sits at the top so zoom/pan controls are easy to reach before interacting with the chart
    toolbar_frame = tk.Frame(root, relief=tk.RAISED, borderwidth=3, bg='lightgray')
    toolbar_frame.pack(side=tk.TOP, fill=tk.X, padx=10, pady=10)
    
    # Instructions label
    instructions = tk.Label(toolbar_frame, 
                           text="Interactive Price Chart | Stock: " + shared_data.symbol,
                           font=("Arial", 11, "bold"), bg="yellow", fg="black")
    instructions.pack(side=tk.TOP, fill=tk.X, pady=(0,5))
    
    # Create matplotlib figure
    fig = Figure(figsize=(16, 11), facecolor='white')
    canvas = FigureCanvasTkAgg(fig, root)
    canvas_widget = canvas.get_tk_widget()
    canvas_widget.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
    
    # Attach the matplotlib navigation toolbar so the user can zoom, pan and save the chart
    toolbar = NavigationToolbar2Tk(canvas, toolbar_frame)
    toolbar.update()
    toolbar.pack(side=tk.TOP, fill=tk.X)
    
    def update_chart():
        fig.clear()
        
        if shared_data.data is None:
            ax = fig.add_subplot(111)
            ax.text(0.5, 0.5, 'No data available\nRun analysis from Control Panel', 
                   ha='center', va='center', transform=ax.transAxes, fontsize=16)
            canvas.draw()
            root.after(3000, update_chart)
            return
        
        # Three-row grid: large price chart on top, MACD in the middle, RSI at the bottom
        gs = fig.add_gridspec(3, 1, height_ratios=[3, 1, 1], hspace=0.3)
        
        df = analyzer.create_features(shared_data.data)
        
        # Limit to the most recent 500 trading days to keep the chart readable at default zoom
        ax1 = fig.add_subplot(gs[0])
        
        recent_periods = min(500, len(df))
        recent_df = df.tail(recent_periods)
        
        ax1.plot(recent_df.index, recent_df['Close'], label='Close Price', linewidth=2.5, color='black')
        ax1.plot(recent_df.index, recent_df['MA_5'], label='MA 5', alpha=0.7, color='red', linewidth=1.5)
        ax1.plot(recent_df.index, recent_df['MA_20'], label='MA 20', alpha=0.7, color='blue', linewidth=1.5)
        ax1.plot(recent_df.index, recent_df['MA_50'], label='MA 50', alpha=0.6, color='green', linewidth=1.5)
        
        if 'BB_Upper' in recent_df.columns and 'BB_Lower' in recent_df.columns:
            # Shaded band between upper and lower Bollinger Bands to visualise volatility range
            ax1.fill_between(recent_df.index, recent_df['BB_Upper'], recent_df['BB_Lower'], 
                           alpha=0.1, color='gray', label='Bollinger Bands')
        
        # Extend the chart into the future with the ML/MACD forecast line and scatter markers
        if shared_data.analysis_results and 'forecast' in shared_data.analysis_results:
            forecast = shared_data.analysis_results['forecast']
            if forecast:
                last_date = df.index[-1]
                last_price = df['Close'].iloc[-1]
                
                # Prepend the current price so the forecast line connects smoothly from today
                pred_dates = [last_date] + [last_date + timedelta(days=point['days']) for point in forecast]
                pred_prices = [last_price] + [point['predicted_price'] for point in forecast]
                
                ax1.plot(pred_dates, pred_prices, 'r-', linewidth=3, 
                        label=f'Predictions ({shared_data.prediction_horizon} days)', alpha=0.9)
                
                forecast_dates = [last_date + timedelta(days=point['days']) for point in forecast]
                forecast_prices = [point['predicted_price'] for point in forecast]
                ax1.scatter(forecast_dates, forecast_prices, color='red', s=80, zorder=6, alpha=0.8)
                
                if forecast_dates:
                    # Highlight the final target date with a star marker so it stands out at a glance
                    target_date = forecast_dates[-1]
                    target_price = forecast_prices[-1]
                    ax1.scatter([target_date], [target_price], 
                               color='darkred', s=250, zorder=7, marker='*',
                               label=f"Target: ${target_price:.2f}")
                
                # Vertical dashed line marks where historical data ends and the forecast begins
                ax1.axvline(x=last_date, color='orange', linestyle='--', alpha=0.7, linewidth=2, 
                           label='Prediction Start')
        
        data_years = (df.index[-1] - df.index[0]).days / 365.25
        training_years = shared_data.analysis_results.get('price', {}).get('training_years', data_years) if shared_data.analysis_results else data_years
        
        ax1.set_title(f'{shared_data.symbol} - Price History & Predictions\n'
                     f'Data: {data_years:.1f} years | Training: {training_years:.1f} years', 
                     fontsize=15, fontweight='bold')
        ax1.legend(loc='upper left', fontsize=11)
        ax1.grid(True, alpha=0.3)
        ax1.tick_params(axis='x', rotation=45)
        ax1.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'${x:.2f}'))
        
        # MACD subplot — sharex links its x-axis to the price chart so zoom/pan stays in sync
        ax2 = fig.add_subplot(gs[1], sharex=ax1)
        if 'MACD' in recent_df.columns and 'MACD_Signal' in recent_df.columns:
            recent_macd = recent_df[['MACD', 'MACD_Signal', 'MACD_Histogram']].dropna()
            if not recent_macd.empty:
                ax2.plot(recent_macd.index, recent_macd['MACD'], label='MACD', color='blue', linewidth=2.5)
                ax2.plot(recent_macd.index, recent_macd['MACD_Signal'], label='Signal', color='red', linewidth=2.5)
                
                # Colour histogram bars green when positive (bullish) and red when negative (bearish)
                colors = ['green' if val > 0 else 'red' for val in recent_macd['MACD_Histogram']]
                ax2.bar(recent_macd.index, recent_macd['MACD_Histogram'], color=colors, alpha=0.4, width=1)
                
                # Overlay the linear regression trend line from predict_macd_trend for visual confirmation
                if shared_data.analysis_results and shared_data.analysis_results.get('macd_trend'):
                    last_30 = recent_macd.tail(30)
                    if len(last_30) >= 20:
                        X = np.arange(len(last_30)).reshape(-1, 1)
                        model = LinearRegression()
                        model.fit(X, last_30['MACD'].values)
                        trend_line = model.predict(X)
                        ax2.plot(last_30.index, trend_line, 'g--', linewidth=2.5, alpha=0.8, label='MACD Trend')
                
                ax2.axhline(y=0, color='black', linestyle='-', alpha=0.5, linewidth=1.5)
                ax2.set_title('MACD (Moving Average Convergence Divergence)', fontsize=12, fontweight='bold')
                ax2.legend(fontsize=10, loc='upper left')
                ax2.grid(True, alpha=0.3)
        
        # RSI subplot — overbought/oversold zones shaded to make threshold breaches immediately visible
        ax3 = fig.add_subplot(gs[2], sharex=ax1)
        recent_rsi = recent_df['RSI'].dropna()
        if not recent_rsi.empty:
            ax3.plot(recent_rsi.index, recent_rsi, color='purple', linewidth=2.5)
            ax3.axhline(y=70, color='r', linestyle='--', alpha=0.7, linewidth=2, label='Overbought (70)')
            ax3.axhline(y=30, color='g', linestyle='--', alpha=0.7, linewidth=2, label='Oversold (30)')
            ax3.fill_between(recent_rsi.index, 70, 100, alpha=0.1, color='red')
            ax3.fill_between(recent_rsi.index, 0, 30, alpha=0.1, color='green')
            ax3.set_title('RSI (Relative Strength Index)', fontsize=12, fontweight='bold')
            ax3.set_ylim(0, 100)
            ax3.legend(fontsize=10, loc='upper left')
            ax3.grid(True, alpha=0.3)
        
        for ax in [ax2, ax3]:
            ax.tick_params(axis='x', rotation=45)
        
        plt.tight_layout()
        canvas.draw()
        root.after(10000, update_chart)  # Redraw the chart every 10 seconds to reflect any new analysis
    
    update_chart()
    root.mainloop()

def create_data_table_window(window_id, x_pos, y_pos, color, content_config):
    """Recent data table window"""
    root = tk.Tk()
    root.title("Recent Stock Data & Predictions")
    root.geometry(f"800x700+{x_pos}+{y_pos}")
    root.configure(bg=color)
    
    title_label = tk.Label(root, text="📋 Recent Data & Future Predictions", 
                          font=("Arial", 14, "bold"), bg=color, fg="white")
    title_label.pack(pady=10)
    
    # Tabbed layout separates historical OHLCV data, forecast rows and model metrics into distinct views
    notebook = ttk.Notebook(root)
    notebook.pack(fill='both', expand=True, padx=10, pady=10)
    
    # Historical Data Tab
    hist_frame = ttk.Frame(notebook)
    notebook.add(hist_frame, text="Historical Data")
    
    hist_columns = ('Date', 'Open', 'High', 'Low', 'Close', 'Volume', 'Change %', 'RSI')
    hist_tree = ttk.Treeview(hist_frame, columns=hist_columns, show='headings', height=15)
    
    for col in hist_columns:
        hist_tree.heading(col, text=col)
        if col == 'Volume':
            hist_tree.column(col, width=100, anchor='center')
        elif col in ['RSI']:
            hist_tree.column(col, width=60, anchor='center')
        else:
            hist_tree.column(col, width=90, anchor='center')
    
    hist_scrollbar = ttk.Scrollbar(hist_frame, orient='vertical', command=hist_tree.yview)
    hist_tree.configure(yscrollcommand=hist_scrollbar.set)
    
    hist_tree.pack(side='left', fill='both', expand=True, padx=5, pady=5)
    hist_scrollbar.pack(side='right', fill='y')
    
    # Predictions Tab
    pred_frame = ttk.Frame(notebook)
    notebook.add(pred_frame, text="Predictions")
    
    pred_columns = ('Date', 'Days From Now', 'Predicted Price', 'Expected Change', 'Change %')
    pred_tree = ttk.Treeview(pred_frame, columns=pred_columns, show='headings', height=15)
    
    for col in pred_columns:
        pred_tree.heading(col, text=col)
        pred_tree.column(col, width=140, anchor='center')
    
    pred_scrollbar = ttk.Scrollbar(pred_frame, orient='vertical', command=pred_tree.yview)
    pred_tree.configure(yscrollcommand=pred_scrollbar.set)
    
    pred_tree.pack(side='left', fill='both', expand=True, padx=5, pady=5)
    pred_scrollbar.pack(side='right', fill='y')
    
    # Model Performance Tab
    perf_frame = ttk.Frame(notebook)
    notebook.add(perf_frame, text="Model Performance")
    
    # Monospaced dark terminal display for raw model metrics, mirroring the summary window style
    perf_text = scrolledtext.ScrolledText(perf_frame, height=20, wrap=tk.WORD, 
                                         font=("Courier", 10), bg="black", fg="lime")
    perf_text.pack(pady=10, padx=10, fill="both", expand=True)
    
    def update_tables():
        # Clear both trees before repopulating so stale rows don't accumulate
        for item in hist_tree.get_children():
            hist_tree.delete(item)
        for item in pred_tree.get_children():
            pred_tree.delete(item)
        
        if shared_data.data is None:
            hist_tree.insert('', 'end', values=('No data available', '', '', '', '', '', '', ''))
            pred_tree.insert('', 'end', values=('No predictions available', '', '', '', ''))
            perf_text.delete(1.0, tk.END)
            perf_text.insert(tk.END, "No model performance data available.\nRun analysis first.")
            root.after(3000, update_tables)
            return
        
        df_features = analyzer.create_features(shared_data.data)
        recent_data = df_features.tail(30)  # Show the last 30 trading days in the historical tab
        
        for i, (date, row) in enumerate(recent_data.iterrows()):
            if i == 0:
                change_pct = 0
            else:
                prev_close = recent_data.iloc[i-1]['Close']
                change_pct = ((row['Close'] - prev_close) / prev_close) * 100
            
            rsi_val = row.get('RSI', 0)
            
            hist_tree.insert('', 'end', values=(
                date.strftime('%Y-%m-%d'),
                f"${row['Open']:.2f}",
                f"${row['High']:.2f}",
                f"${row['Low']:.2f}",
                f"${row['Close']:.2f}",
                f"{row['Volume']:,.0f}",
                f"{change_pct:+.2f}%",
                f"{rsi_val:.1f}" if not pd.isna(rsi_val) else "N/A"
            ))
        
        if shared_data.analysis_results and 'forecast' in shared_data.analysis_results:
            forecast = shared_data.analysis_results['forecast']
            current_price = shared_data.analysis_results['trend']['current_price']
            
            # Calculate each forecast point's change relative to today's price, not the previous forecast point
            for point in forecast:
                expected_change = point['predicted_price'] - current_price
                change_pct = (expected_change / current_price) * 100
                
                pred_tree.insert('', 'end', values=(
                    point['date'],
                    f"{point['days']} days",
                    f"${point['predicted_price']:.2f}",
                    f"${expected_change:+.2f}",
                    f"{change_pct:+.2f}%"
                ))
        
        perf_text.delete(1.0, tk.END)
        if shared_data.analysis_results:
            results = shared_data.analysis_results
            direction = results['direction']
            price = results['price']
            trend = results['trend']
            macd_trend = results.get('macd_trend')
            prediction_source = results.get('prediction_source', 'ML Model')
            
            perf_info = f"""
MODEL PERFORMANCE METRICS
========================

Dataset Information:
- Stock Symbol: {shared_data.symbol}
- Full Data: {trend['total_days']} days ({trend['data_years']:.1f} years)
- Training Data: {price['training_years']:.1f} years
- Training Samples: {price.get('training_samples', 'N/A')}
- Horizon: {shared_data.prediction_horizon} days

PREDICTION SOURCE: {prediction_source}

Direction Prediction:
- Confidence: {direction['confidence']:.2f}%
- Prediction: {direction['direction']}

Price Prediction:
- Predicted Price: ${price['predicted_price']:.2f}
- Expected Change: {price['price_change_pct']:+.2f}%
- Current Price: ${trend['current_price']:.2f}
"""
            
            if macd_trend:
                perf_info += f"""
MACD Trend Analysis:
- Direction: {macd_trend['direction']}
- Confidence: {macd_trend['confidence']:.1f}%
- MACD Falling: {"YES ⚠️" if macd_trend['is_macd_falling'] else "NO"}
- MACD Slope: {macd_trend['macd_slope']:.4f}
- Signal Slope: {macd_trend['signal_slope']:.4f}
- Histogram: {macd_trend['histogram_trend']}
- MACD Price: ${macd_trend['predicted_price']:.2f}
- MACD Change: {macd_trend['price_change_pct']:+.2f}%
"""
            
            perf_info += f"""
Recent Technical Indicators:
- Current RSI: {recent_data['RSI'].iloc[-1]:.1f}
- Current MA Signal: {trend['ma_signal']}
- MACD: {recent_data['MACD'].iloc[-1]:.3f}
- MACD Signal: {recent_data['MACD_Signal'].iloc[-1]:.3f}

Last Updated: {results['timestamp']}
"""
            
            perf_text.insert(tk.END, perf_info)
        
        root.after(5000, update_tables)  # Re-populate the tables every 5 seconds to catch new results
    
    update_tables()
    root.mainloop()

def launch_stock_analysis():
    """Launch the stock analysis system after successful login"""
    
    # Each window gets an id, screen position and background colour; the function reference determines its content
    windows_config = [
        {
            "id": 1, "x": 50, "y": 50, "color": "#2C3E50",
            "content": {
                "title": "Control Panel",
                "custom_function": create_control_window
            }
        },
        {
            "id": 2, "x": 500, "y": 50, "color": "#34495E",
            "content": {
                "title": "Analysis Summary",
                "custom_function": create_summary_window
            }
        },
        {
            "id": 3, "x": 1050, "y": 50, "color": "#27AE60",
            "content": {
                "title": "Interactive Chart",
                "custom_function": create_chart_window
            }
        },
        {
            "id": 4, "x": 300, "y": 450, "color": "#8E44AD",
            "content": {
                "title": "Data & Performance",
                "custom_function": create_data_table_window
            }
        }
    ]
    
    threads = []
    
    for config in windows_config:
        # Each window runs in its own daemon thread so they can all display simultaneously
        thread = threading.Thread(
            target=config["content"]["custom_function"],
            args=(config["id"], config["x"], config["y"], config["color"], config["content"]),
            daemon=True
        )
        threads.append(thread)
        thread.start()
        time.sleep(0.3)  # Small delay between launches to avoid race conditions during tkinter initialisation
    
    print("🚀 Enhanced Stock Analysis Multi-Window Interface Started!")
    print("\n📊 Windows opened:")
    print("  1. Control Panel - Search ANY stock & select prediction horizons")
    print("  2. Analysis Summary - Final predictions with MACD fallback") 
    print("  3. Interactive Chart - ZOOM-ENABLED with MACD & RSI only")
    print("  4. Data & Performance - Historical data, predictions, and metrics")
    print("\n✨ KEY FEATURES:")
    print("  🎯 Smart Prediction Logic:")
    print("     • Uses ML models for longer-term predictions")
    print("     • Falls back to MACD analysis when ML confidence is low")
    print("     • MACD falling detection for short-term bearish signals")
    print("     • Forces non-zero price changes (realistic market behavior)")
    
    try:
        for thread in threads:
            thread.join()
    except KeyboardInterrupt:
        print("\n👋 Closing all windows...")

# ============================================================================
# MAIN ENTRY POINT
# ============================================================================

if __name__ == "__main__":
    # Instantiate and run the login screen; the stock analysis windows open only after a successful login
    app = LoginApp()
    app.run()