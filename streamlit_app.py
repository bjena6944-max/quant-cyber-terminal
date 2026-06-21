import streamlit as st
import os
from dotenv import load_dotenv
load_dotenv()

# For deployment, Streamlit secrets will override
try:
    api_key_1 = os.getenv("GEMINI_API_KEY") or st.secrets.get("GEMINI_API_KEY")
except:
    api_key_1 = os.getenv("GEMINI_API_KEY")

import yfinance as yf
import streamlit.components.v1 as components
import google.generativeai as genai
from datetime import datetime
import pandas as pd
import numpy as np
import requests
import time
import plotly.graph_objects as go
import warnings
warnings.filterwarnings('ignore')

# ===== REAL-TIME ML IMPORTS (with graceful fallback) =====
try:
    import websocket
    import threading
    import json
    from sklearn.ensemble import RandomForestRegressor
    from sklearn.preprocessing import StandardScaler
    ML_AVAILABLE = True
except ImportError:
    ML_AVAILABLE = False
    websocket = None
    threading = None
    json = None
    RandomForestRegressor = None
    StandardScaler = None
    st.warning("⚠️ Real-time ML requires 'websocket-client'. Install with: pip install websocket-client")

# ==========================================
# PAGE CONFIG
# ==========================================
st.set_page_config(
    page_title="NEONALPHA — Institutional Quant Intelligence",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==========================================
# GOOGLE SEARCH CONSOLE VERIFICATION META TAG
# ==========================================
st.markdown("""
    <meta name="google-site-verification" content="qGPnSzkacfMR9iCcJpfegkA4u7MnNv5cm7QHrRHD2W4" />
""", unsafe_allow_html=True)

# ==========================================
# GOOGLE TAG MANAGER (For Verification) - SCRIPT VERSION
# ==========================================
st.markdown("""
    <!-- Google Tag Manager -->
    <script>
    (function(w,d,s,l,i){
        w[l]=w[l]||[];
        w[l].push({'gtm.start': new Date().getTime(), event:'gtm.js'});
        var f=d.getElementsByTagName(s)[0],
            j=d.createElement(s),
            dl=l!='dataLayer'?'&l='+l:'';
        j.async=true;
        j.src='https://www.googletagmanager.com/gtm.js?id='+i+dl;
        f.parentNode.insertBefore(j,f);
    })(window,document,'script','dataLayer','GTM-MNCD3WR3');
    </script>
    <!-- End Google Tag Manager -->
""", unsafe_allow_html=True)

# ==========================================
# GOOGLE TAG MANAGER (For Verification) - NOSCRIPT VERSION
# ==========================================
st.markdown("""
    <noscript>
        <iframe src="https://www.googletagmanager.com/ns.html?id=GTM-MNCD3WR3"
        height="0" width="0" style="display:none;visibility:hidden"></iframe>
    </noscript>
""", unsafe_allow_html=True)

# ==========================================
# SERVE GOOGLE VERIFICATION HTML FILE (FALLBACK)
# ==========================================
verification_file = "googlea939c6e0ed88f9e2.html"
if os.path.exists(verification_file):
    try:
        with open(verification_file, "r", encoding="utf-8") as f:
            content = f.read()
        content = content.replace("<html>", "").replace("</html>", "")
        content = content.replace("<head>", "").replace("</head>", "")
        content = content.replace("<body>", "").replace("</body>", "")
        st.markdown(content, unsafe_allow_html=True)
    except:
        pass

# ==========================================
# CUSTOM CSS
# ==========================================
st.markdown("""
    <style>
        .stApp { background-color: #0d0e15; color: #e0e6ed; }
        h1, h2, h3 { color: #00ffcc !important; text-shadow: 0 0 10px #00ffcc; font-family: 'Courier New', monospace; }
        section[data-testid="stSidebar"] { background-color: #121420 !important; border-right: 2px solid #00ffcc !important; box-shadow: 5px 0px 15px rgba(0, 255, 204, 0.3) !important; }
        div[data-testid="stMetricValue"] { color: #39ff14 !important; text-shadow: 0 0 8px #39ff14; font-size: 26px !important; font-weight: bold; }
        div[data-testid="stMetricLabel"] { color: #00bfff !important; font-family: 'Courier New', monospace; }
        .stButton>button { background: linear-gradient(45deg, #00ffcc, #00bfff) !important; color: #0d0e15 !important; border: none !important; box-shadow: 0 0 15px rgba(0, 255, 204, 0.6) !important; font-weight: bold; width: 100%; }
        .stButton>button:hover { transform: scale(1.02); box-shadow: 0 0 25px rgba(0, 255, 204, 0.9) !important; }
        button[data-baseweb="tab"] { color: #e0e6ed !important; font-size: 16px !important; font-weight: bold !important; }
        button[aria-selected="true"] { color: #00ffcc !important; border-bottom-color: #00ffcc !important; text-shadow: 0 0 5px #00ffcc; }
        .chart-wrapper {
            border: 2px solid #00ffcc !important;
            border-radius: 8px !important;
            overflow: hidden !important;
            background-color: #0b0f19 !important;
            box-shadow: 0 0 10px rgba(0, 255, 204, 0.3) !important;
        }
        .cyber-wrapper {
            border: 3px solid #00ffcc !important;
            border-radius: 12px !important;
            overflow: hidden !important;
            background-color: #0b0f19 !important;
            box-shadow: 0 0 20px rgba(0, 255, 204, 0.4) !important;
        }
        iframe {
            border: none !important;
            outline: none !important;
        }
        .tradingview-widget-container iframe,
        .tradingview-widget-container div {
            border: none !important;
            outline: none !important;
        }
        .agent-box {
            background: #121420;
            border-radius: 8px;
            padding: 15px;
            margin: 10px 0;
            border-left: 4px solid #00ffcc;
        }
        .final-signal {
            background: #0b0f19;
            border: 2px solid #ff007f;
            border-radius: 12px;
            padding: 20px;
            margin: 15px 0;
            box-shadow: 0 0 20px rgba(255, 0, 127, 0.3);
        }
        .stImage img {
            filter: drop-shadow(0 0 15px rgba(0, 255, 204, 0.5));
            border-radius: 8px;
            background: transparent !important;
        }
        .brand-container {
            display: flex;
            align-items: center;
            gap: 20px;
            height: 100%;
        }
        .brand-name {
            font-size: 32px;
            color: #00ffcc;
            text-shadow: 0 0 25px #00ffcc;
            font-weight: bold;
            font-family: 'Courier New', monospace;
        }
        .brand-tagline {
            font-size: 14px;
            color: #ff007f;
            text-shadow: 0 0 15px #ff007f;
            letter-spacing: 4px;
            opacity: 0.8;
            margin-top: 5px;
        }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# FUNCTIONS
# ==========================================

def get_live_price(symbol):
    try:
        ticker = yf.Ticker(symbol)
        data = ticker.history(period="1d", interval="1m")
        if not data.empty:
            return data['Close'].iloc[-1]
        return None
    except:
        return None

def get_fear_greed():
    try:
        url = "https://api.alternative.me/fng/"
        response = requests.get(url)
        data = response.json()
        if data and 'data' in data:
            value = int(data['data'][0]['value'])
            classification = data['data'][0]['value_classification']
            return value, classification
        return None, None
    except:
        return None, None

@st.cache_data(ttl=60)
def get_market_data():
    try:
        url = "https://api.coingecko.com/api/v3/coins/markets"
        params = {
            "vs_currency": "usd",
            "order": "market_cap_desc",
            "per_page": 10,
            "page": 1,
            "sparkline": False
        }
        response = requests.get(url, params=params)
        data = response.json()
        df = pd.DataFrame(data)
        df = df[['name', 'symbol', 'current_price', 'price_change_percentage_24h', 'market_cap', 'total_volume']]
        df.columns = ['Coin', 'Symbol', 'Price (USD)', '24h Change %', 'Market Cap', 'Volume']
        df['Symbol'] = df['Symbol'].str.upper()
        return df
    except:
        return pd.DataFrame()

@st.cache_data(ttl=60)
def get_heatmap_data():
    try:
        url = "https://api.coingecko.com/api/v3/coins/markets"
        params = {
            "vs_currency": "usd",
            "order": "market_cap_desc",
            "per_page": 20,
            "page": 1,
            "sparkline": False
        }
        response = requests.get(url, params=params)
        data = response.json()
        heatmap_data = []
        for coin in data:
            heatmap_data.append({
                'name': coin['symbol'].upper(),
                'change': coin['price_change_percentage_24h'] or 0,
                'market_cap': coin['market_cap'] or 0
            })
        return pd.DataFrame(heatmap_data)
    except:
        return pd.DataFrame()

def generate_multi_agent_signal(api_key, price_data, total_capital, risk_percent, fear_greed_tuple):
    if not api_key:
        return None, None
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-2.5-flash')
        fg_val, fg_label = fear_greed_tuple if fear_greed_tuple else (50, 'Neutral')
        prompt = f"""
You are an elite Institutional Trading Desk with multiple specialists. Your task is to analyze the given data and produce a comprehensive trading signal.

=== MARKET DATA ===
Asset: {price_data['asset']}
Current Price: ${price_data['price']:.2f}
RSI (14): {price_data['rsi']:.2f}
MACD: {price_data['macd']:.4f}
Signal Line: {price_data['signal_line']:.4f}
Bollinger Upper: ${price_data['bb_upper']:.2f}
Bollinger Lower: ${price_data['bb_lower']:.2f}
Bollinger Middle: ${price_data['bb_middle']:.2f}
EMA 9: ${price_data['ema9']:.2f}
SMA 20: ${price_data['sma20']:.2f}
Recent High (24h): ${price_data['recent_high']:.2f}
Recent Low (24h): ${price_data['recent_low']:.2f}
Volatility: ${price_data['volatility']:.2f}
Fear & Greed Index: {fg_val}/100 ({fg_label})
Total Capital: ${total_capital:,.0f}
Risk per trade: {risk_percent}%

=== YOUR OUTPUT FORMAT ===
You MUST respond in the EXACT format below.

--- TECHNICAL ANALYSIS ---
Technical Score: [0-100]
Trend: [Uptrend/Downtrend/Sideways]
Support: $[price]
Resistance: $[price]
Signal: [BUY/SELL/HOLD]
Confidence: [High/Medium/Low]

--- RISK MANAGEMENT ---
Position Size: [units]
Stop Loss: $[price]
Take Profit: $[price]
Risk Score: [1-10]
VaR: $[amount]

--- SENTIMENT ANALYSIS ---
Sentiment Score: [0-100]
Market Regime: [Bullish/Bearish/Neutral/Volatile]
Bias: [Overbought/Oversold/Neutral]
Recommendation: [Aggressive Buy/Cautious Buy/Hold/Cautious Sell/Aggressive Sell]

--- PATTERN RECOGNITION ---
Patterns: [pattern names]
Confidence: [High/Medium/Low]
Implied Move: [direction and price target]

--- FINAL TRADING SIGNAL ---
FINAL SIGNAL: [BUY/SELL/HOLD]
CONFIDENCE: [XX%]
ENTRY: $[price]
STOP LOSS: $[price]
TAKE PROFIT: $[price]
R/R: 1:[ratio]
RATIONALE: [2-3 lines summary]
RISK WARNING: [critical risks if any]

IMPORTANT: Provide ALL sections. Use only the exact headers shown. Fill all fields with concrete numbers.
If confidence is below 60%, signal HOLD.
"""
        response = model.generate_content(prompt)
        output_text = response.text

        sections = {}
        current_section = None
        lines = output_text.split('\n')
        for line in lines:
            if line.startswith('---') and line.endswith('---'):
                section_name = line.strip('- ')
                current_section = section_name
                sections[current_section] = []
            elif current_section and line.strip():
                sections[current_section].append(line.strip())

        tech_report = '\n'.join(sections.get('TECHNICAL ANALYSIS', [])) or 'Technical analysis not available.'
        risk_report = '\n'.join(sections.get('RISK MANAGEMENT', [])) or 'Risk analysis not available.'
        sent_report = '\n'.join(sections.get('SENTIMENT ANALYSIS', [])) or 'Sentiment analysis not available.'
        pat_report = '\n'.join(sections.get('PATTERN RECOGNITION', [])) or 'Pattern analysis not available.'
        
        final_text = ''
        if 'FINAL TRADING SIGNAL' in sections:
            final_text = '\n'.join(sections['FINAL TRADING SIGNAL'])
        elif 'FINAL' in sections:
            final_text = '\n'.join(sections['FINAL'])
        else:
            final_text = output_text

        agent_outputs = {
            'technical': tech_report,
            'risk': risk_report,
            'sentiment': sent_report,
            'pattern': pat_report
        }
        return final_text, agent_outputs

    except Exception as e:
        error_msg = str(e)
        if "429" in error_msg or "quota" in error_msg.lower():
            st.warning("⚠️ Gemini API quota exceeded. AI signal temporarily unavailable. Backtest & ML still work!")
            return None, None
        else:
            st.error(f"Multi-Agent System Error: {error_msg}")
            return None, None

def run_manual_backtest(symbol, interval, period, params):
    try:
        ticker = yf.Ticker(symbol)
        data = ticker.history(period=period, interval=interval)
        if data.empty:
            return None, "No data fetched", None
        if len(data) < 50:
            return None, "Insufficient data (need at least 50 bars)", None
        data['fast_ma'] = data['Close'].rolling(params['fast_len']).mean()
        data['slow_ma'] = data['Close'].rolling(params['slow_len']).mean()
        delta = data['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(params['rsi_len']).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(params['rsi_len']).mean()
        rs = gain / loss
        data['rsi'] = 100 - (100 / (1 + rs))
        high_low = data['High'] - data['Low']
        high_close = (data['High'] - data['Close'].shift()).abs()
        low_close = (data['Low'] - data['Close'].shift()).abs()
        ranges = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
        data['atr'] = ranges.rolling(14).mean()
        data['bb_mid'] = data['Close'].rolling(20).mean()
        data['bb_std'] = data['Close'].rolling(20).std()
        data['bb_lower'] = data['bb_mid'] - 2 * data['bb_std']
        data['bb_upper'] = data['bb_mid'] + 2 * data['bb_std']
        data['signal'] = 0
        long_cond = (data['fast_ma'] > data['slow_ma']) & (data['fast_ma'].shift(1) <= data['slow_ma'].shift(1))
        long_cond |= (data['rsi'] < params['rsi_os']) & (data['Close'] > data['bb_lower'])
        data.loc[long_cond, 'signal'] = 1
        short_cond = (data['fast_ma'] < data['slow_ma']) & (data['fast_ma'].shift(1) >= data['slow_ma'].shift(1))
        short_cond |= (data['rsi'] > params['rsi_ob']) & (data['Close'] < data['bb_upper'])
        data.loc[short_cond, 'signal'] = -1
        cash = 10000
        position = 0
        entry_price = 0
        trades = []
        equity = [cash]
        for i in range(1, len(data)):
            price = data['Close'].iloc[i]
            sig = data['signal'].iloc[i]
            if sig == 1 and position == 0:
                position = cash / price
                cash = 0
                entry_price = price
                trades.append({'EntryTime': data.index[i], 'EntryPrice': price, 'Size': position, 'ExitTime': None, 'ExitPrice': None, 'PnL': 0})
            elif sig == -1 and position > 0:
                cash = position * price
                position = 0
                trades[-1]['ExitTime'] = data.index[i]
                trades[-1]['ExitPrice'] = price
                trades[-1]['PnL'] = (price - entry_price) * (cash / price if cash > 0 else 1)
            equity.append(cash + position * price if position > 0 else cash)
        if position > 0:
            last_price = data['Close'].iloc[-1]
            cash = position * last_price
            trades[-1]['ExitTime'] = data.index[-1]
            trades[-1]['ExitPrice'] = last_price
            trades[-1]['PnL'] = (last_price - entry_price) * (cash / last_price)
            position = 0
        for t in trades:
            if t['ExitPrice'] is not None:
                t['PnL'] = (t['ExitPrice'] - t['EntryPrice']) * t['Size']
                t['ReturnPct'] = (t['PnL'] / 10000) * 100
        trades_df = pd.DataFrame(trades)
        equity_curve = pd.DataFrame({'Equity': equity}, index=data.index[:len(equity)])
        total_trades = len(trades_df)
        if total_trades > 0:
            win_trades = len(trades_df[trades_df['PnL'] > 0])
            win_rate = (win_trades / total_trades) * 100
            total_return = ((equity[-1] - 10000) / 10000) * 100
            avg_return = trades_df['PnL'].mean()
            max_drawdown = ((equity_curve['Equity'].max() - equity_curve['Equity']) / equity_curve['Equity'].max() * 100).max()
        else:
            win_rate = 0; total_return = 0; avg_return = 0; max_drawdown = 0
        stats = {
            'Return [%]': total_return,
            'Win Rate [%]': win_rate,
            'Max Drawdown [%]': max_drawdown,
            'Avg Trade': avg_return,
            'Total Trades': total_trades
        }
        return stats, trades_df, equity_curve
    except Exception as e:
        return None, f"Error: {str(e)}", None

if ML_AVAILABLE:
    class LiveMLPredictor:
        def __init__(self, symbol="btcusdt"):
            self.symbol = symbol.lower()
            self.data = []
            self.model = None
            self.scaler = StandardScaler()
            self.last_price = None
            self.prediction = None
            self.confidence = 0
            self.is_running = False
            self.ws = None
            self.thread = None
        def start(self):
            if self.is_running:
                return
            self.is_running = True
            self.thread = threading.Thread(target=self._run_websocket, daemon=True)
            self.thread.start()
            st.success(f"✅ Real-time ML started for {self.symbol.upper()}")
        def stop(self):
            self.is_running = False
            if self.ws:
                self.ws.close()
            st.info("⏹️ Real-time ML stopped")
        def _run_websocket(self):
            websocket.enableTrace(False)
            ws_url = f"wss://stream.binance.com:9443/ws/{self.symbol}@kline_1m"
            self.ws = websocket.WebSocketApp(
                ws_url,
                on_message=self._on_message,
                on_error=self._on_error,
                on_close=self._on_close
            )
            self.ws.run_forever()
        def _on_message(self, ws, message):
            try:
                data = json.loads(message)
                kline = data['k']
                candle = {
                    'timestamp': datetime.fromtimestamp(kline['t'] / 1000),
                    'open': float(kline['o']),
                    'high': float(kline['h']),
                    'low': float(kline['l']),
                    'close': float(kline['c']),
                    'volume': float(kline['v'])
                }
                self.last_price = candle['close']
                self.data.append(candle)
                if len(self.data) > 150:
                    self.data.pop(0)
                if len(self.data) >= 50:
                    self._train_and_predict()
            except Exception as e:
                print(f"WebSocket parse error: {e}")
        def _on_error(self, ws, error):
            print(f"WebSocket error: {error}")
        def _on_close(self, ws, close_status_code, close_msg):
            print(f"WebSocket closed: {close_status_code} - {close_msg}")
            self.is_running = False
        def _train_and_predict(self):
            try:
                if len(self.data) < 50:
                    return
                df = pd.DataFrame(self.data)
                df['returns'] = df['close'].pct_change()
                df['rsi'] = self._calculate_rsi(df['close'])
                df['volatility'] = df['high'] - df['low']
                exp1 = df['close'].ewm(span=12, adjust=False).mean()
                exp2 = df['close'].ewm(span=26, adjust=False).mean()
                df['macd'] = exp1 - exp2
                df['macd_signal'] = df['macd'].ewm(span=9, adjust=False).mean()
                df['macd_hist'] = df['macd'] - df['macd_signal']
                df['volume_change'] = df['volume'].pct_change()
                df = df.dropna()
                if len(df) < 30:
                    return
                df['target'] = df['close'].shift(-1)
                df = df.dropna()
                if len(df) < 20:
                    return
                features = ['returns', 'rsi', 'volatility', 'macd', 'macd_hist', 'volume_change']
                X = df[features].values
                y = df['target'].values
                X_scaled = self.scaler.fit_transform(X)
                self.model = RandomForestRegressor(n_estimators=50, max_depth=5, random_state=42, n_jobs=-1)
                self.model.fit(X_scaled, y)
                latest_features = df[features].iloc[-1:].values
                latest_scaled = self.scaler.transform(latest_features)
                self.prediction = self.model.predict(latest_scaled)[0]
                tree_preds = [tree.predict(latest_scaled)[0] for tree in self.model.estimators_]
                self.confidence = 1 - (np.std(tree_preds) / self.last_price)
                self.confidence = min(max(self.confidence, 0), 1)
            except Exception as e:
                print(f"ML prediction error: {e}")
        def _calculate_rsi(self, prices, period=14):
            delta = prices.diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
            rs = gain / loss
            rsi = 100 - (100 / (1 + rs))
            return rsi
        def get_latest_data(self):
            return {
                'current_price': self.last_price,
                'prediction': self.prediction,
                'confidence': self.confidence,
                'data': pd.DataFrame(self.data),
                'is_running': self.is_running
            }

# ==========================================
# BRANDING
# ==========================================

col_logo, col_text = st.columns([1, 5])

with col_logo:
    st.image("NEONALPHA.png", width=80)

with col_text:
    st.markdown("""
        <div class="brand-container">
            <span class="brand-name">NEONALPHA</span>
            <span class="brand-tagline">INSTITUTIONAL QUANT INTELLIGENCE</span>
        </div>
    """, unsafe_allow_html=True)

st.markdown("---")

# ==========================================
# GOOGLE SEO - Organization Schema Markup
# ==========================================
st.markdown("""
    <script type="application/ld+json">
    {
        "@context": "https://schema.org",
        "@type": "Organization",
        "name": "NEONALPHA",
        "url": "https://quant-cyber-terminal-jvos7vnhrnbfmkxfd5bdhm.streamlit.app",
        "logo": "https://quant-cyber-terminal-jvos7vnhrnbfmkxfd5bdhm.streamlit.app/NEONALPHA.png"
    }
    </script>
""", unsafe_allow_html=True)

# ==========================================
# SIDEBAR
# ==========================================
st.sidebar.markdown("<h2 style='color:#00ffcc; text-shadow: 0 0 5px #00ffcc;'>🎛️ CONTROL PANEL</h2>", unsafe_allow_html=True)
api_key_1 = st.sidebar.text_input("🔑 Primary Gemini Key", type="password")
api_key_2 = st.sidebar.text_input("🔑 Backup Gemini Key", type="password")

market_type = st.sidebar.selectbox("🌐 Market Segment", ["Crypto Currency", "Indian Stocks"])
timeframe_choice = st.sidebar.selectbox("⏱️ Trading Timeframe", ["1 Hour (1h)", "15 Minutes (15m)", "5 Minutes (5m)", "1 Day (1d)"])

timeframe_mapping = {"5 Minutes (5m)": "5m", "15 Minutes (15m)": "15m", "1 Hour (1h)": "1h", "1 Day (1d)": "1d"}
selected_interval = timeframe_mapping[timeframe_choice]
data_period = "2d" if selected_interval in ["5m", "15m"] else ("1mo" if market_type == "Indian Stocks" else "5d")

if market_type == "Crypto Currency":
    crypto_options = [
        "BTC-USD (Bitcoin)", "ETH-USD (Ethereum)", "SOL-USD (Solana)", 
        "BNB-USD (Binance Coin)", "XRP-USD (Ripple)", "ADA-USD (Cardano)", 
        "DOT-USD (Polkadot)", "DOGE-USD (Dogecoin)", "AVAX-USD (Avalanche)", 
        "LINK-USD (Chainlink)", "MATIC-USD (Polygon)", "NEAR-USD (Near Protocol)",
        "SUI-USD (Sui Network)", "APT-USD (Aptos)", "OP-USD (Optimism)", 
        "ARB-USD (Arbitrum)", "LTC-USD (Litecoin)", "ATOM-USD (Cosmos)"
    ]
    selected_crypto = st.sidebar.selectbox("🎫 Select Crypto Pair", crypto_options)
    yf_ticker = selected_crypto.split(" ")[0].strip()
    tv_symbol_for_binance = yf_ticker.replace("-", "").strip()
    tv_url_symbol = f"BINANCE%3A{tv_symbol_for_binance}"
else:
    user_ticker = st.sidebar.text_input("🎫 Stock Ticker", value="RELIANCE.NS")
    yf_ticker = user_ticker.upper().strip()
    tv_url_symbol = f"NSE%3A{yf_ticker.split('.')[0].strip()}"

st.sidebar.markdown("---")
st.sidebar.markdown("<h3 style='color:#00ffcc;'>⚖️ POSITION SIZER</h3>", unsafe_allow_html=True)
total_capital = st.sidebar.number_input("Total Capital", min_value=100, value=10000)
risk_percent = st.sidebar.slider("Risk Per Trade (%)", min_value=0.5, max_value=5.0, value=1.0, step=0.5)
user_query = st.sidebar.text_area("⚙️ Custom AI Instructions", value="Provide 2-3 fast intraday trade setups with tight stoploss.")

# FEAR & GREED
st.sidebar.markdown("---")
st.sidebar.markdown("<h3 style='color:#00ffcc;'>😨 FEAR & GREED INDEX</h3>", unsafe_allow_html=True)
fg_value, fg_label = get_fear_greed()
if fg_value:
    if fg_value <= 25:
        color = "#ff4444"; emoji = "😱"
    elif fg_value <= 45:
        color = "#ff8800"; emoji = "😰"
    elif fg_value <= 55:
        color = "#ffcc00"; emoji = "😐"
    elif fg_value <= 75:
        color = "#88ff44"; emoji = "😊"
    else:
        color = "#44ff44"; emoji = "🚀"
    st.sidebar.markdown(f"""
        <div style='background:#121420; border:2px solid {color}; padding:15px; border-radius:10px; text-align:center;'>
            <h2 style='color:{color}; margin:0;'>{emoji} {fg_value}/100</h2>
            <p style='margin:0; color:#e0e6ed;'>{fg_label}</p>
        </div>
    """, unsafe_allow_html=True)
else:
    st.sidebar.info("Fear & Greed data unavailable")

# AUTO-REFRESH
st.sidebar.markdown("---")
st.sidebar.markdown("<h3 style='color:#00ffcc;'>🔄 AUTO REFRESH</h3>", unsafe_allow_html=True)
refresh_interval = st.sidebar.selectbox("Refresh Interval", ["Off", "10 seconds", "30 seconds", "1 minute", "5 minutes"])
if refresh_interval != "Off":
    interval_map = {"10 seconds": 10, "30 seconds": 30, "1 minute": 60, "5 minutes": 300}
    seconds = interval_map[refresh_interval]
    st.markdown(f"""
        <meta http-equiv="refresh" content="{seconds}">
    """, unsafe_allow_html=True)
    st.sidebar.success(f"🔄 Auto-refresh every {refresh_interval}")
    if 'last_refresh' not in st.session_state:
        st.session_state.last_refresh = datetime.now()
    elapsed = (datetime.now() - st.session_state.last_refresh).seconds
    remaining = seconds - elapsed
    if remaining > 0:
        st.sidebar.caption(f"⏱️ Next refresh in {remaining}s")

execute_analysis = st.sidebar.button("⚡ EXECUTE ALL MATRICES")

# ==========================================
# LIVE PRICE TICKER
# ==========================================
price_placeholder = st.empty()
with price_placeholder.container():
    ticker_to_use = yf_ticker if market_type == "Crypto Currency" else "RELIANCE.NS"
    current_price = get_live_price(ticker_to_use)
    col1, col2, col3 = st.columns([2, 1, 1])
    if current_price:
        col1.metric("💰 LIVE PRICE", f"${current_price:,.2f}")
        change = ((current_price - 65000)/65000*100) if market_type == "Crypto Currency" else 0
        col2.metric("📊 24H CHANGE", f"{change:+.2f}%")
        col3.metric("⏱️ UPDATED", datetime.now().strftime("%H:%M:%S"))
    else:
        col1.metric("💰 LIVE PRICE", "Loading...")
        col2.metric("📊 24H CHANGE", "--")
        col3.metric("⏱️ UPDATED", datetime.now().strftime("%H:%M:%S"))
st.markdown("---")

# ==========================================
# TABS
# ==========================================
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📊 LIVE TRADING DESK", 
    "🧠 ADVANCED QUANT LAB", 
    "🚨 RISK & WATCHLIST", 
    "🌍 MARKET OVERVIEW",
    "🤖 REAL-TIME ML PREDICTOR"
])

# ==========================================
# TAB 1: LIVE TRADING DESK
# ==========================================
with tab1:
    st.markdown(f"### 📈 MULTI-TIMEFRAME INTERACTIVE MATRIX [{yf_ticker}]")
    def get_tv_iframe(symbol, interval):
        return f"""
        <iframe src="https://s.tradingview.com/widgetembed/?frameElementId=tradingview_chart&symbol={symbol}&interval={interval}&symboledit=0&saveimage=0&toolbarbg=131722&theme=dark&style=1&timezone=Asia%2FKolkata"
                width="100%" height="340" style="border: none !important;"></iframe>
        """
    row1_col1, row1_col2 = st.columns(2)
    with row1_col1:
        st.markdown("<p style='color:#00ffcc; margin-bottom:5px; font-weight:bold;'>🏹 1 HOUR (1H) EXECUTION</p>", unsafe_allow_html=True)
        st.markdown('<div class="chart-wrapper">', unsafe_allow_html=True)
        components.html(get_tv_iframe(tv_url_symbol, "60"), height=350, scrolling=False)
        st.markdown('</div>', unsafe_allow_html=True)
    with row1_col2:
        st.markdown("<p style='color:#00ffcc; margin-bottom:5px; font-weight:bold;'>⚡ 4 HOURS (4H) STRUCTURE</p>", unsafe_allow_html=True)
        st.markdown('<div class="chart-wrapper">', unsafe_allow_html=True)
        components.html(get_tv_iframe(tv_url_symbol, "240"), height=350, scrolling=False)
        st.markdown('</div>', unsafe_allow_html=True)
    row2_col1, row2_col2 = st.columns(2)
    with row2_col1:
        st.markdown("<p style='color:#00ffcc; margin-bottom:5px; font-weight:bold;'>⏱️ 12 HOURS (12H) MOMENTUM</p>", unsafe_allow_html=True)
        st.markdown('<div class="chart-wrapper">', unsafe_allow_html=True)
        components.html(get_tv_iframe(tv_url_symbol, "720"), height=350, scrolling=False)
        st.markdown('</div>', unsafe_allow_html=True)
    with row2_col2:
        st.markdown("<p style='color:#00ffcc; margin-bottom:5px; font-weight:bold;'>📅 1 DAY (1D) TREND</p>", unsafe_allow_html=True)
        st.markdown('<div class="chart-wrapper">', unsafe_allow_html=True)
        components.html(get_tv_iframe(tv_url_symbol, "D"), height=350, scrolling=False)
        st.markdown('</div>', unsafe_allow_html=True)
    st.write("---")
    st.markdown("### 📊 LIVE CYBERPUNK CRYPTO TERMINAL")
    ticker_raw = yf_ticker.replace("-", "").replace(".NS", "").upper()
    tradingview_html_main = f"""
    <div class="cyber-wrapper" style="height:620px; width:100%;">
      <div class="tradingview-widget-container" style="height:100%; width:100%;">
        <div id="tradingview_chart_main" style="height:100%; width:100%;"></div>
        <script type="text/javascript" src="https://s3.tradingview.com/tv.js"></script>
        <script type="text/javascript">
        new TradingView.widget({{
          "autosize": true,
          "symbol": "BINANCE:{ticker_raw if market_type == 'Crypto Currency' else tv_url_symbol.replace('NSE%3A', '')}",
          "interval": "720",
          "timezone": "Asia/Kolkata",
          "theme": "dark",
          "style": "1",
          "locale": "en",
          "toolbar_bg": "#0b0f19",
          "enable_publishing": false,
          "hide_side_toolbar": false,
          "allow_symbol_change": true,
          "details": true,
          "hotlist": true,
          "calendar": true,
          "studies": [
            "RSI@tv-basicstudies",
            "MACD@tv-basicstudies",
            "BollingerBands@tv-basicstudies"
          ],
          "container_id": "tradingview_chart_main"
        }});
        </script>
      </div>
    </div>
    """
    components.html(tradingview_html_main, height=630, scrolling=False)
    st.write("---")
    ai_signal_placeholder = st.empty()
    if not execute_analysis:
        with ai_signal_placeholder.container():
            st.markdown("### 🤖 INSTITUTIONAL AI ANALYST SIGNAL")
            st.info("👆 Click **⚡ EXECUTE ALL MATRICES** in the sidebar to get AI trade signals and full metrics.")

# ==========================================
# TAB 4: MARKET OVERVIEW
# ==========================================
with tab4:
    st.markdown("### 🌍 CRYPTO MARKET OVERVIEW")
    market_df = get_market_data()
    if not market_df.empty:
        for idx, row in market_df.iterrows():
            col1, col2, col3, col4, col5 = st.columns([2, 1, 2, 2, 2])
            col1.write(f"**{row['Coin']}**")
            col2.write(row['Symbol'])
            col3.write(f"${row['Price (USD)']:,.2f}")
            change = row['24h Change %']
            if change > 0:
                col4.markdown(f'<span style="color:#39ff14;">+{change:.2f}%</span>', unsafe_allow_html=True)
            else:
                col4.markdown(f'<span style="color:#ff4444;">{change:.2f}%</span>', unsafe_allow_html=True)
            col5.write(f"${row['Volume']/1e9:.1f}B")
            st.divider()
    else:
        st.info("Market data fetch nahi ho pa raha hai. API limit ho sakti hai.")
    st.markdown("#### 📊 MARKET HEATMAP")
    heatmap_df = get_heatmap_data()
    if not heatmap_df.empty:
        cols = st.columns(5)
        for idx, row in heatmap_df.iterrows():
            if idx >= 20:
                break
            col_idx = idx % 5
            with cols[col_idx]:
                change = row['change']
                if change > 0:
                    opacity = min(abs(change) / 20, 1)
                    bg_color = f"rgba(57, 255, 20, {opacity})"
                else:
                    opacity = min(abs(change) / 20, 1)
                    bg_color = f"rgba(255, 68, 68, {opacity})"
                st.markdown(f"""
                    <div style='background:{bg_color}; padding:10px; border-radius:5px; margin:5px 0; text-align:center;'>
                        <b style='color:white;'>{row['name']}</b><br>
                        <span style='color:white;'>{change:.1f}%</span>
                    </div>
                """, unsafe_allow_html=True)
    else:
        st.info("Heatmap data unavailable")

# ==========================================
# TAB 5: REAL-TIME ML PREDICTOR
# ==========================================
with tab5:
    st.markdown("### 🤖 REAL-TIME ML PRICE PREDICTOR")
    if not ML_AVAILABLE:
        st.error("❌ 'websocket-client' library not installed. Please run: `pip install websocket-client` and restart.")
        st.info("ℹ️ ML predictions will be available after installation. You can still use other features.")
    else:
        st.caption("⚡ Binance WebSocket से live data fetch + ML model (Random Forest) से next candle prediction")
        if 'ml_predictor' not in st.session_state:
            st.session_state.ml_predictor = None
        ml_symbol = st.selectbox("Select Symbol for ML Prediction", ["BTCUSDT", "ETHUSDT", "SOLUSDT", "BNBUSDT"], index=0, key="ml_symbol")
        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button("🚀 Start Real-time ML", use_container_width=True):
                if st.session_state.ml_predictor is None:
                    st.session_state.ml_predictor = LiveMLPredictor(symbol=ml_symbol)
                st.session_state.ml_predictor.start()
                st.rerun()
        with col2:
            if st.button("⏹️ Stop ML", use_container_width=True):
                if st.session_state.ml_predictor:
                    st.session_state.ml_predictor.stop()
                    st.session_state.ml_predictor = None
                st.rerun()
        with col3:
            st.markdown("### ")
        if st.session_state.ml_predictor and st.session_state.ml_predictor.is_running:
            data = st.session_state.ml_predictor.get_latest_data()
            if data['current_price']:
                c1, c2, c3, c4 = st.columns(4)
                c1.metric("💰 Current Price", f"${data['current_price']:,.2f}")
                if data['prediction']:
                    pred_change = ((data['prediction'] - data['current_price']) / data['current_price']) * 100
                    c2.metric("🔮 Predicted (Next Candle)", f"${data['prediction']:,.2f}", f"{pred_change:+.2f}%")
                    c3.metric("🎯 Confidence", f"{data['confidence']*100:.1f}%")
                    if pred_change > 0.1:
                        c4.metric("📈 Signal", "🟢 BULLISH", "Strong Buy")
                    elif pred_change < -0.1:
                        c4.metric("📉 Signal", "🔴 BEARISH", "Strong Sell")
                    else:
                        c4.metric("⚖️ Signal", "🟡 NEUTRAL", "Hold")
                if not data['data'].empty:
                    df = data['data'].tail(50)
                    fig = go.Figure()
                    fig.add_trace(go.Candlestick(
                        x=df['timestamp'],
                        open=df['open'],
                        high=df['high'],
                        low=df['low'],
                        close=df['close'],
                        name="Live Price",
                        increasing_line_color='#26a69a',
                        decreasing_line_color='#ef5350'
                    ))
                    if data['prediction']:
                        last_time = df['timestamp'].iloc[-1]
                        next_time = last_time + pd.Timedelta(minutes=1)
                        fig.add_trace(go.Scatter(
                            x=[last_time, next_time],
                            y=[data['current_price'], data['prediction']],
                            mode='lines+markers',
                            name='Predicted',
                            line=dict(color='#ff007f', width=2, dash='dash'),
                            marker=dict(size=12, color='#ff007f')
                        ))
                        std_dev = (data['current_price'] * (1 - data['confidence'])) * 0.5
                        fig.add_trace(go.Scatter(
                            x=[next_time, next_time],
                            y=[data['prediction'] - std_dev, data['prediction'] + std_dev],
                            mode='markers',
                            name='Confidence Band',
                            marker=dict(size=10, color='rgba(255, 0, 127, 0.3)'),
                            showlegend=True
                        ))
                    fig.update_layout(
                        template='plotly_dark',
                        height=500,
                        xaxis_title='Time',
                        yaxis_title='Price (USD)',
                        margin=dict(l=10, r=10, t=20, b=20),
                        xaxis_rangeslider_visible=False
                    )
                    st.plotly_chart(fig, use_container_width=True)
                    with st.expander("📊 Recent Data (Last 10 candles)", expanded=False):
                        display_df = df.tail(10)[['timestamp', 'open', 'high', 'low', 'close', 'volume']]
                        display_df.columns = ['Time', 'Open', 'High', 'Low', 'Close', 'Volume']
                        display_df['Volume'] = display_df['Volume'].apply(lambda x: f"{x:,.0f}")
                        st.dataframe(display_df, use_container_width=True)
            else:
                st.info("⏳ Waiting for data...")
        else:
            st.info("👆 Click **'Start Real-time ML'** to begin live prediction.")
            st.markdown("""
            ---
            ### ℹ️ How it works:
            - **Data Source:** Binance WebSocket (1-minute candles)
            - **Model:** Random Forest Regressor
            - **Features:** RSI, MACD, Volatility, Returns, Volume
            - **Prediction:** Next candle's closing price
            - **Updates:** Every 1 minute (real-time)
            """)

# ==========================================
# TAB 2: ADVANCED QUANT LAB
# ==========================================
with tab2:
    if execute_analysis:
        grid_placeholder = st.empty()
    else:
        st.info("📊 Click **⚡ EXECUTE ALL MATRICES** to load quant indicators and backtest results.")

    st.markdown("---")
    st.markdown("### ⚡ Advanced Backtest Engine (Quant X Ultimate Strategy)")

    with st.expander("⚙️ Strategy Parameters", expanded=True):
        col1, col2, col3 = st.columns(3)
        with col1:
            fast_len = st.number_input("Fast MA Length", min_value=1, max_value=50, value=9, key="bt_fast")
            slow_len = st.number_input("Slow MA Length", min_value=1, max_value=100, value=21, key="bt_slow")
            rsi_len = st.number_input("RSI Length", min_value=1, max_value=50, value=14, key="bt_rsi")
            rsi_ob = st.number_input("RSI Overbought", min_value=50, max_value=90, value=70, key="bt_ob")
            rsi_os = st.number_input("RSI Oversold", min_value=10, max_value=50, value=30, key="bt_os")
        with col2:
            atr_multiplier = st.number_input("ATR Multiplier (SL)", min_value=0.5, max_value=5.0, value=1.5, step=0.1, key="bt_atr")
            rr_ratio = st.number_input("Risk/Reward Ratio", min_value=1.0, max_value=5.0, value=2.0, step=0.5, key="bt_rr")
            risk_per_trade = st.number_input("Risk Per Trade (%)", min_value=0.1, max_value=5.0, value=1.0, step=0.1, key="bt_risk")
        with col3:
            use_partial = st.checkbox("Enable Partial Exits", value=True, key="bt_partial")
            tp1_percent = st.number_input("TP1 %", min_value=0.1, max_value=5.0, value=1.0, step=0.1, key="bt_tp1") if use_partial else 0.0
            backtest_period = st.selectbox("Backtest Period", ["1mo", "3mo", "6mo", "1y", "2y"], index=0, key="bt_period")

    if st.button("🚀 Run Advanced Backtest", key="run_bt", use_container_width=True):
        with st.spinner("Running full backtest..."):
            params = {
                'fast_len': fast_len,
                'slow_len': slow_len,
                'rsi_len': rsi_len,
                'rsi_ob': rsi_ob,
                'rsi_os': rsi_os,
                'atr_multiplier': atr_multiplier,
                'rr_ratio': rr_ratio,
                'risk_per_trade': risk_per_trade,
                'use_partial_exits': use_partial,
                'tp1_percent': tp1_percent,
            }
            stats, trades, equity = run_manual_backtest(yf_ticker, selected_interval, backtest_period, params)
            if stats is None:
                st.error(f"Backtest failed: {trades}")
            else:
                st.success("✅ Backtest completed!")
                col1, col2, col3, col4 = st.columns(4)
                col1.metric("Total Return %", f"{stats['Return [%]']:.2f}%")
                col2.metric("Win Rate %", f"{stats['Win Rate [%]']:.2f}%")
                col3.metric("Total Trades", f"{stats['Total Trades']}")
                col4.metric("Max Drawdown %", f"{stats['Max Drawdown [%]']:.2f}%")
                st.markdown("#### 📈 Equity Curve")
                fig = go.Figure()
                fig.add_trace(go.Scatter(x=equity.index, y=equity['Equity'], mode='lines', name='Equity', line=dict(color='#00ffcc')))
                fig.update_layout(template='plotly_dark', height=400, margin=dict(l=10, r=10, t=20, b=20))
                st.plotly_chart(fig, use_container_width=True)
                st.markdown("#### 📋 Trade Log")
                if trades is not None and not trades.empty:
                    display_cols = ['EntryTime', 'ExitTime', 'EntryPrice', 'ExitPrice', 'PnL', 'ReturnPct']
                    existing = [c for c in display_cols if c in trades.columns]
                    trades_display = trades[existing].copy()
                    if 'ReturnPct' in trades_display:
                        trades_display['ReturnPct'] = trades_display['ReturnPct'] * 100
                        trades_display.rename(columns={'ReturnPct': 'Return %'}, inplace=True)
                    if 'PnL' in trades_display:
                        trades_display.rename(columns={'PnL': 'PnL ($)'}, inplace=True)
                    st.dataframe(trades_display.style.format({
                        'PnL ($)': '${:.2f}',
                        'Return %': '{:.2f}%'
                    }), use_container_width=True)
                else:
                    st.info("No trades executed.")
                csv = trades.to_csv(index=False) if trades is not None and not trades.empty else ""
                if csv:
                    st.download_button(
                        label="📥 Download Trade Log (CSV)",
                        data=csv,
                        file_name=f"backtest_trades_{yf_ticker}_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
                        mime="text/csv"
                    )

# ==========================================
# MAIN ANALYSIS - EXECUTE BUTTON
# ==========================================
if execute_analysis:
    if not api_key_1:
        st.error("⚠️ Primary Gemini API Key missing! Please add your API key in the sidebar.")
        with st.spinner("Loading data for analysis..."):
            try:
                stock = yf.Ticker(yf_ticker)
                hist = stock.history(period=data_period, interval=selected_interval, auto_adjust=True)
                if not hist.empty:
                    with tab2:
                        st.markdown("### 🧪 MULTI-INDICATOR SCANNER GRID")
                        c1, c2, c3, c4 = st.columns(4)
                        hist['EMA_9'] = hist['Close'].rolling(window=9).mean()
                        hist['SMA_20'] = hist['Close'].rolling(window=20).mean()
                        delta = hist['Close'].diff()
                        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
                        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
                        rs = gain / (loss + 1e-10)
                        hist['RSI'] = 100 - (100 / (1 + rs))
                        hist['EMA_12'] = hist['Close'].rolling(window=12).mean()
                        hist['EMA_26'] = hist['Close'].rolling(window=26).mean()
                        hist['MACD'] = hist['EMA_12'] - hist['EMA_26']
                        hist['Signal_Line'] = hist['MACD'].rolling(window=9).mean()
                        hist['BB_Middle'] = hist['Close'].rolling(window=20).mean()
                        hist['BB_Std'] = hist['Close'].rolling(window=20).std()
                        hist['BB_Upper'] = hist['BB_Middle'] + (hist['BB_Std'] * 2)
                        hist['BB_Lower'] = hist['BB_Middle'] - (hist['BB_Std'] * 2)
                        current_price = hist['Close'].iloc[-1]
                        latest_rsi = hist['RSI'].iloc[-1]
                        latest_macd = hist['MACD'].iloc[-1]
                        latest_signal = hist['Signal_Line'].iloc[-1]
                        bb_upper = hist['BB_Upper'].iloc[-1]
                        bb_lower = hist['BB_Lower'].iloc[-1]
                        c1.metric(label="LIVE PRICE", value=f"${current_price:.2f}")
                        c2.metric(label="RSI MATRIX", value=f"{latest_rsi:.2f}")
                        c3.metric(label="MACD VALUE", value=f"{latest_macd:.4f}")
                        c4.metric(label="BOLLINGER UPPER", value=f"${bb_upper:.2f}")
                        st.markdown("#### ⚡ SIGNAL ALIGNMENT ENGINE")
                        col_a, col_b = st.columns(2)
                        if latest_macd > latest_signal:
                            col_a.markdown("<div style='border:1px solid #39ff14; padding:15px; border-radius:5px;'><b style='color:#39ff14;'>📈 MACD: BULLISH CROSSOVER</b></div>", unsafe_allow_html=True)
                        else:
                            col_a.markdown("<div style='border:1px solid #ff007f; padding:15px; border-radius:5px;'><b style='color:#ff007f;'>📉 MACD: BEARISH DOWNTREND</b></div>", unsafe_allow_html=True)
                        if current_price >= bb_upper * 0.98:
                            col_b.markdown("<div style='border:1px solid #ff007f; padding:15px; border-radius:5px;'><b style='color:#ff007f;'>🛑 OVERBOUGHT</b></div>", unsafe_allow_html=True)
                        elif current_price <= bb_lower * 1.02:
                            col_b.markdown("<div style='border:1px solid #39ff14; padding:15px; border-radius:5px;'><b style='color:#39ff14;'>🟢 OVERSOLD</b></div>", unsafe_allow_html=True)
                        else:
                            col_b.markdown("<div style='border:1px solid #00bfff; padding:15px; border-radius:5px;'><b style='color:#00bfff;'>🔵 COMPRESSION ZONE</b></div>", unsafe_allow_html=True)
            except Exception as e:
                st.error(f"Data Error: {str(e)}")
    else:
        with st.spinner("🧠 Analyzing with Institutional AI Agents..."):
            try:
                stock = yf.Ticker(yf_ticker)
                hist = stock.history(period=data_period, interval=selected_interval, auto_adjust=True)
                if not hist.empty:
                    hist['EMA_9'] = hist['Close'].rolling(window=9).mean()
                    hist['SMA_20'] = hist['Close'].rolling(window=20).mean()
                    delta = hist['Close'].diff()
                    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
                    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
                    rs = gain / (loss + 1e-10)
                    hist['RSI'] = 100 - (100 / (1 + rs))
                    hist['EMA_12'] = hist['Close'].rolling(window=12).mean()
                    hist['EMA_26'] = hist['Close'].rolling(window=26).mean()
                    hist['MACD'] = hist['EMA_12'] - hist['EMA_26']
                    hist['Signal_Line'] = hist['MACD'].rolling(window=9).mean()
                    hist['BB_Middle'] = hist['Close'].rolling(window=20).mean()
                    hist['BB_Std'] = hist['Close'].rolling(window=20).std()
                    hist['BB_Upper'] = hist['BB_Middle'] + (hist['BB_Std'] * 2)
                    hist['BB_Lower'] = hist['BB_Middle'] - (hist['BB_Std'] * 2)
                    current_price = hist['Close'].iloc[-1]
                    latest_rsi = hist['RSI'].iloc[-1]
                    latest_macd = hist['MACD'].iloc[-1]
                    latest_signal = hist['Signal_Line'].iloc[-1]
                    bb_upper = hist['BB_Upper'].iloc[-1]
                    bb_lower = hist['BB_Lower'].iloc[-1]
                    bb_middle = hist['BB_Middle'].iloc[-1]
                    ema9 = hist['EMA_9'].iloc[-1]
                    sma20 = hist['SMA_20'].iloc[-1]
                    recent_high = hist['High'].iloc[-24:].max() 
                    recent_low = hist['Low'].iloc[-24:].min()
                    volatility = recent_high - recent_low

                    price_data = {
                        'asset': yf_ticker,
                        'price': current_price,
                        'rsi': latest_rsi,
                        'macd': latest_macd,
                        'signal_line': latest_signal,
                        'bb_upper': bb_upper,
                        'bb_lower': bb_lower,
                        'bb_middle': bb_middle,
                        'ema9': ema9,
                        'sma20': sma20,
                        'recent_high': recent_high,
                        'recent_low': recent_low,
                        'volatility': volatility
                    }
                    fear_greed_tuple = (fg_value, fg_label) if fg_value else (50, 'Neutral')

                    final_signal, agent_outputs = generate_multi_agent_signal(
                        api_key_1, price_data, total_capital, risk_percent, fear_greed_tuple
                    )
                    if final_signal is None and api_key_2:
                        final_signal, agent_outputs = generate_multi_agent_signal(
                            api_key_2, price_data, total_capital, risk_percent, fear_greed_tuple
                        )

                    with tab1:
                        ai_signal_placeholder.empty()
                        with ai_signal_placeholder.container():
                            st.markdown("### 🤖 INSTITUTIONAL AI ANALYST SIGNAL")
                            if final_signal:
                                st.markdown('<div class="final-signal">', unsafe_allow_html=True)
                                st.markdown("#### 🎯 FINAL TRADING DECISION")
                                st.markdown(final_signal)
                                st.markdown('</div>', unsafe_allow_html=True)
                                with st.expander("🔬 Technical Analyst Report", expanded=False):
                                    st.markdown(f'<div class="agent-box">{agent_outputs["technical"]}</div>', unsafe_allow_html=True)
                                with st.expander("🛡️ Risk Manager Report", expanded=False):
                                    st.markdown(f'<div class="agent-box">{agent_outputs["risk"]}</div>', unsafe_allow_html=True)
                                with st.expander("📊 Sentiment Analyst Report", expanded=False):
                                    st.markdown(f'<div class="agent-box">{agent_outputs["sentiment"]}</div>', unsafe_allow_html=True)
                                with st.expander("📈 Pattern Recognition Report", expanded=False):
                                    st.markdown(f'<div class="agent-box">{agent_outputs["pattern"]}</div>', unsafe_allow_html=True)
                                st.download_button(
                                    label="📥 DOWNLOAD COMPLETE ANALYSIS (TXT)", 
                                    data=f"=== FINAL SIGNAL ===\n{final_signal}\n\n=== TECHNICAL ANALYSIS ===\n{agent_outputs['technical']}\n\n=== RISK ANALYSIS ===\n{agent_outputs['risk']}\n\n=== SENTIMENT ANALYSIS ===\n{agent_outputs['sentiment']}\n\n=== PATTERN ANALYSIS ===\n{agent_outputs['pattern']}",
                                    file_name=f"Quant_AI_Report_{yf_ticker}_{datetime.now().strftime('%Y%m%d_%H%M')}.txt", 
                                    mime="text/plain"
                                )
                            else:
                                st.warning("⚠️ Multi-Agent system could not generate a signal. Please check API key or try again.")

                    with tab2:
                        st.markdown("### 🧪 MULTI-INDICATOR SCANNER GRID")
                        c1, c2, c3, c4 = st.columns(4)
                        c1.metric(label="LIVE PRICE", value=f"${current_price:.2f}")
                        c2.metric(label="RSI MATRIX", value=f"{latest_rsi:.2f}")
                        c3.metric(label="MACD VALUE", value=f"{latest_macd:.4f}")
                        c4.metric(label="BOLLINGER UPPER", value=f"${bb_upper:.2f}")
                        st.markdown("#### ⚡ SIGNAL ALIGNMENT ENGINE")
                        col_a, col_b = st.columns(2)
                        if latest_macd > latest_signal:
                            col_a.markdown("<div style='border:1px solid #39ff14; padding:15px; border-radius:5px;'><b style='color:#39ff14;'>📈 MACD: BULLISH CROSSOVER</b></div>", unsafe_allow_html=True)
                        else:
                            col_a.markdown("<div style='border:1px solid #ff007f; padding:15px; border-radius:5px;'><b style='color:#ff007f;'>📉 MACD: BEARISH DOWNTREND</b></div>", unsafe_allow_html=True)
                        if current_price >= bb_upper * 0.98:
                            col_b.markdown("<div style='border:1px solid #ff007f; padding:15px; border-radius:5px;'><b style='color:#ff007f;'>🛑 OVERBOUGHT</b></div>", unsafe_allow_html=True)
                        elif current_price <= bb_lower * 1.02:
                            col_b.markdown("<div style='border:1px solid #39ff14; padding:15px; border-radius:5px;'><b style='color:#39ff14;'>🟢 OVERSOLD</b></div>", unsafe_allow_html=True)
                        else:
                            col_b.markdown("<div style='border:1px solid #00bfff; padding:15px; border-radius:5px;'><b style='color:#00bfff;'>🔵 COMPRESSION ZONE</b></div>", unsafe_allow_html=True)
                        st.markdown("---")
                        st.markdown("### ⏪ STRATEGY BACKTESTER ENGINE (Past 20 Candles)")
                        hist_20 = hist.tail(20).copy()
                        hist_20['Signal'] = np.where(hist_20['EMA_9'] > hist_20['SMA_20'], 1, -1)
                        hist_20['Returns'] = hist_20['Close'].pct_change()
                        hist_20['Strat_Returns'] = hist_20['Returns'] * hist_20['Signal'].shift(1)
                        total_win = (hist_20['Strat_Returns'] > 0).sum()
                        total_loss = (hist_20['Strat_Returns'] <= 0).sum()
                        win_ratio = (total_win / (total_win + total_loss)) * 100 if (total_win + total_loss) > 0 else 0.0
                        b1, b2, b3 = st.columns(3)
                        b1.metric(label="WIN-RATE %", value=f"{win_ratio:.1f}%")
                        b2.metric(label="WINNING TRADES", value=f"{total_win}")
                        b3.metric(label="NET ALPHA", value=f"+{hist_20['Strat_Returns'].sum()*100:.2f}%" if hist_20['Strat_Returns'].sum() >= 0 else f"{hist_20['Strat_Returns'].sum()*100:.2f}%")

                    with tab3:
                        st.markdown("### 🚨 RISK MANAGEMENT PROFILE")
                        allowed_risk_cash = total_capital * (risk_percent / 100)
                        estimated_stop_distance = abs(current_price - recent_low) if latest_rsi <= 50 else abs(recent_high - current_price)
                        if estimated_stop_distance == 0: estimated_stop_distance = current_price * 0.01
                        calculated_position_size = allowed_risk_cash / estimated_stop_distance
                        r1, r2, r3 = st.columns(3)
                        r1.metric(label="RISK CAPITAL", value=f"${allowed_risk_cash:.2f}")
                        r2.metric(label="POSITION SIZE", value=f"{calculated_position_size:.3f} Units")
                        r3.metric(label="24H VOLATILITY", value=f"${volatility:.2f}")
                        st.markdown("---")
                        col_left, col_right = st.columns([1, 2])
                        with col_left:
                            st.markdown("#### 🎭 SENTIMENT INDEX")
                            sentiment_score = int(latest_rsi)
                            if sentiment_score > 70: label, color = "EXTREME GREED 🔥", "#ff007f"
                            elif sentiment_score < 30: label, color = "EXTREME FEAR 😨", "#39ff14"
                            else: label, color = "NEUTRAL ⚖️", "#00ffcc"
                            st.markdown(f"""
                                <div style='background:#121420; border:2px solid {color}; padding:22px; border-radius:8px; text-align:center;'>
                                    <h3 style='color:{color}!important; margin:0;'>{label}</h3>
                                    <p style='margin:5px 0 0 0; font-size:15px; color:#e0e6ed;'>Score: {sentiment_score}/100</p>
                                </div>
                            """, unsafe_allow_html=True)
                        with col_right:
                            st.markdown("#### 📊 ORDER BOOK SIMULATOR")
                            prices = [current_price * (1 + x) for x in [+0.002, +0.001, -0.001, -0.002]]
                            volumes = [np.random.randint(12, 160) for _ in range(4)]
                            types = ['🔴 ASK (Sell)', '🔴 ASK (Sell)', '🟢 BID (Buy)', '🟢 BID (Buy)']
                            order_book = pd.DataFrame({
                                'Order Flow': types, 
                                'Price': [f"${p:.2f}" for p in prices], 
                                'Volume': volumes
                            })
                            st.table(order_book)
                        st.markdown("---")
                        st.markdown("### 🎫 WATCHLIST")
                        watchlist_data = pd.DataFrame({
                            'Pair': ['BTC-USD', 'ETH-USD', 'SOL-USD', 'RELIANCE.NS'],
                            'Trend': ['🔴 Bearish', '🟢 Bounce', '🟢 Momentum', '🔴 Reject'],
                            'Volatility': ['High ATR', 'Stable', 'Extreme', 'Low']
                        })
                        st.dataframe(watchlist_data, use_container_width=True)
            except Exception as e:
                st.error(f"🚨 Analysis Error: {str(e)}")
else:
    with tab2:
        st.info("📊 Click **⚡ EXECUTE ALL MATRICES** to load quant indicators.")
    with tab3:
        st.info("🛡️ Click **⚡ EXECUTE ALL MATRICES** to see risk profile.")
    with tab4:
        pass
    with tab5:
        pass

# ==========================================
# PINE SCRIPT EDITOR
# ==========================================
st.write("---")
st.markdown("<h3 style='color: #00ffcc; text-shadow:0 0 5px #00ffcc;'>🌲 Advanced Pine Script Strategy Editor</h3>", unsafe_allow_html=True)
advance_pine_template = """//@version=6
strategy("⚡ QUANT X ULTIMATE STRATEGY", overlay=true, initial_capital=10000)
// ... (full Pine Script code) ...
"""
user_pine = st.text_area(
    "TradingView Pine Script Editor:", 
    value=advance_pine_template, 
    height=300,
    key="pro_pine_editor_key"
)
if 'show_the_chart' not in st.session_state:
    st.session_state.show_the_chart = False
col_exec1, col_exec2 = st.columns([2, 1])
with col_exec1:
    if st.button("⚡ Execute Strategy On Chart", key="btn_exec_pro_pine", use_container_width=True):
        st.session_state.show_the_chart = True
with col_exec2:
    if st.button("🗑️ Reset Editor Dashboard", use_container_width=True):
        st.session_state.show_the_chart = False
if st.session_state.show_the_chart:
    st.info("Pine Script execution visual will be shown here (Plotly chart).")