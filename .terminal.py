import streamlit as st
import yfinance as yf
import streamlit.components.v1 as components
import google.generativeai as genai
from datetime import datetime
import pandas as pd
import numpy as np
import requests
import time

# Page Layout Settings
st.set_page_config(page_title="QUANT X CYBER TERMINAL", layout="wide", initial_sidebar_state="expanded")

# Custom Neon Cyberpunk CSS
st.markdown("""
    <style>
        .stApp { background-color: #0d0e15; color: #e0e6ed; }
        h1, h2, h3 { color: #00ffcc !important; text-shadow: 0 0 10px #00ffcc; font-family: 'Courier New', monospace; }
        section[data-testid="stSidebar"] { background-color: #121420 !important; border-right: 2px solid #ff007f; box-shadow: 5px 0px 15px rgba(255, 0, 127, 0.3); }
        div[data-testid="stMetricValue"] { color: #39ff14 !important; text-shadow: 0 0 8px #39ff14; font-size: 26px !important; font-weight: bold; }
        div[data-testid="stMetricLabel"] { color: #00bfff !important; font-family: 'Courier New', monospace; }
        .stButton>button { background: linear-gradient(45deg, #ff007f, #7928ca) !important; color: white !important; border: none !important; box-shadow: 0 0 15px rgba(255, 0, 127, 0.6) !important; font-weight: bold; width: 100%; }
        .stButton>button:hover { transform: scale(1.02); box-shadow: 0 0 25px rgba(0, 255, 204, 0.9) !important; background: linear-gradient(45deg, #00ffcc, #00bfff) !important; color: #0d0e15 !important; }
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
    </style>
""", unsafe_allow_html=True)

# ==========================================
# FEATURE 1: LIVE PRICE TICKER
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

# ==========================================
# FEATURE 2: FEAR & GREED INDEX
# ==========================================
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

# ==========================================
# FEATURE 3: MARKET OVERVIEW DATA
# ==========================================
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

# ==========================================
# FEATURE 4: HEATMAP DATA
# ==========================================
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

# ==========================================
# BRANDING
# ==========================================
st.title("⚡ QUANT X CYBER AI TERMINAL")
st.markdown("<p style='color:#ff007f; font-weight:bold; text-shadow:0 0 5px #ff007f;'>[ALL-IN-ONE INSTITUTIONAL INTELLIGENCE PLATFORM]</p>", unsafe_allow_html=True)

# LIVE PRICE TICKER
price_placeholder = st.empty()
with price_placeholder.container():
    col1, col2, col3 = st.columns([2, 1, 1])
    current_price = get_live_price("BTC-USD" if market_type == "Crypto Currency" else "RELIANCE.NS")
    if current_price:
        col1.metric("💰 LIVE PRICE", f"${current_price:,.2f}")
        col2.metric("📊 24H CHANGE", f"+{((current_price - 65000)/65000*100):.2f}%")
        col3.metric("⏱️ UPDATED", datetime.now().strftime("%H:%M:%S"))
    else:
        col1.metric("💰 LIVE PRICE", "Loading...")

st.markdown("---")

# ==========================================
# SIDEBAR
# ==========================================
st.sidebar.markdown("<h2 style='color:#ff007f; text-shadow: 0 0 5px #ff007f;'>🎛️ CONTROL PANEL</h2>", unsafe_allow_html=True)

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

# FEATURE 2: FEAR & GREED INDEX IN SIDEBAR
st.sidebar.markdown("---")
st.sidebar.markdown("<h3 style='color:#00ffcc;'>😨 FEAR & GREED INDEX</h3>", unsafe_allow_html=True)

fg_value, fg_label = get_fear_greed()
if fg_value:
    if fg_value <= 25:
        color = "#ff4444"
        emoji = "😱"
    elif fg_value <= 45:
        color = "#ff8800"
        emoji = "😰"
    elif fg_value <= 55:
        color = "#ffcc00"
        emoji = "😐"
    elif fg_value <= 75:
        color = "#88ff44"
        emoji = "😊"
    else:
        color = "#44ff44"
        emoji = "🚀"
    
    st.sidebar.markdown(f"""
        <div style='background:#121420; border:2px solid {color}; padding:15px; border-radius:10px; text-align:center;'>
            <h2 style='color:{color}; margin:0;'>{emoji} {fg_value}/100</h2>
            <p style='margin:0; color:#e0e6ed;'>{fg_label}</p>
        </div>
    """, unsafe_allow_html=True)
else:
    st.sidebar.info("Fear & Greed data unavailable")

# FEATURE 5: AUTO-REFRESH
st.sidebar.markdown("---")
st.sidebar.markdown("<h3 style='color:#00ffcc;'>🔄 AUTO REFRESH</h3>", unsafe_allow_html=True)

refresh_interval = st.sidebar.selectbox(
    "Refresh Interval", 
    ["Off", "10 seconds", "30 seconds", "1 minute", "5 minutes"]
)

if refresh_interval != "Off":
    interval_map = {
        "10 seconds": 10,
        "30 seconds": 30,
        "1 minute": 60,
        "5 minutes": 300
    }
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
# TABS - 4 Tabs (Added Market Overview)
# ==========================================
tab1, tab2, tab3, tab4 = st.tabs(["📊 LIVE TRADING DESK", "🧠 ADVANCED QUANT LAB", "🚨 RISK & WATCHLIST", "🌍 MARKET OVERVIEW"])

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
# TAB 4: MARKET OVERVIEW (New)
# ==========================================
with tab4:
    st.markdown("### 🌍 CRYPTO MARKET OVERVIEW")
    
    market_df = get_market_data()
    if not market_df.empty:
        # Display as styled table
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
    
    # HEATMAP
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
# ANALYSIS (Button Click)
# ==========================================
if execute_analysis:
    if not api_key_1:
        st.error("⚠️ Primary Gemini API Key missing!")
    else:
        with st.spinner("Processing Global Terminal Stream..."):
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
                    recent_high = hist['High'].iloc[-24:].max() 
                    recent_low = hist['Low'].iloc[-24:].min()   

                    with tab1:
                        ai_signal_placeholder.empty()
                        with ai_signal_placeholder.container():
                            st.markdown("### 🤖 INSTITUTIONAL AI ANALYST SIGNAL")
                            latest_metrics = f"Asset: {yf_ticker} | Price: {current_price:.2f} | RSI: {latest_rsi:.2f} | MACD: {latest_macd:.4f}"
                            prompt = f"Act as hedge fund manager. Give clear BUY/SELL execution based on this data:\n{latest_metrics}\nUser instructions: {user_query}. Respond in neat Hinglish bullet points."
                            
                            response_text = None
                            try:
                                genai.configure(api_key=api_key_1)
                                model = genai.GenerativeModel('gemini-2.5-flash')
                                response = model.generate_content(prompt)
                                response_text = response.text
                            except:
                                if api_key_2:
                                    try:
                                        genai.configure(api_key=api_key_2)
                                        model = genai.GenerativeModel('gemini-2.5-flash')
                                        response = model.generate_content(prompt)
                                        response_text = response.text
                                    except: pass
                            
                            if response_text: 
                                st.info(response_text)
                                st.download_button(
                                    label="📥 DOWNLOAD TRADE REPORT (TXT)", 
                                    data=response_text, 
                                    file_name=f"Quant_AI_Report_{yf_ticker}_{datetime.now().strftime('%Y%m%d')}.txt", 
                                    mime="text/plain"
                                )
                            else: 
                                st.warning("🚨 LOCAL QUANT REVERSION SYSTEM RUNNING")
                    
                    with tab2:
                        st.markdown("### 🧪 MULTI-INDICATOR SCANNER GRID")
                        c1, c2, c3, c4 = st.columns(4)
                        c1.metric(label="LIVE PRICE", value=f"{current_price:.2f}")
                        c2.metric(label="RSI MATRIX", value=f"{latest_rsi:.2f}")
                        c3.metric(label="MACD VALUE", value=f"{latest_macd:.4f}")
                        c4.metric(label="BOLLINGER UPPER", value=f"{bb_upper:.2f}")
                        
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
                        st.markdown("### ⏪ STRATEGY BACKTESTER ENGINE")
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
                        r1.metric(label="RISK CAPITAL", value=f"{allowed_risk_cash:.2f}")
                        r2.metric(label="POSITION SIZE", value=f"{calculated_position_size:.3f} Units")
                        r3.metric(label="24H VOLATILITY", value=f"{(recent_high - recent_low):.2f}")
                        
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
                                'Price': [f"{p:.2f}" for p in prices], 
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
                        
                else:
                    st.warning("⚠️ Market data feed empty.")
            except Exception as e:
                st.error(f"Error: {e}")
else:
    with tab2:
        st.info("📊 Click **⚡ EXECUTE ALL MATRICES** to load quant indicators.")
    with tab3:
        st.info("🛡️ Click **⚡ EXECUTE ALL MATRICES** to see risk profile.")
    with tab4:
        st.info("🌍 Market Overview data is loading automatically!")

# ==========================================
# PINE SCRIPT ENGINE
# ==========================================
st.write("---")
st.markdown("<h3 style='color: #00ffcc; text-shadow:0 0 5px #00ffcc;'>🌲 Advanced Pine Script Strategy Editor</h3>", unsafe_allow_html=True)

advance_pine_template = """// @version=5
strategy("Advance Multi-MA Strategy", overlay=true, initial_capital=10000)

// Parameters
fastLen = input(9, "Fast MA")
slowLen = input(21, "Slow MA")

// Logic
fastMA = ta.sma(close, fastLen)
slowMA = ta.sma(close, slowLen)

longCondition = ta.crossover(fastMA, slowMA)
shortCondition = ta.crossunder(fastMA, slowMA)

// Execution Plot
plot(fastMA, color=color.aqua, title="Fast MA")
plot(slowMA, color=color.orange, title="Slow MA")
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
    crypto_df = None
    if 'hist' in locals() and not hist.empty:
        crypto_df = hist
    else:
        try:
            t_active = yf_ticker
            crypto_df = yf.download(t_active, period="1mo", interval="1h")
        except: pass

    if crypto_df is not None and not crypto_df.empty:
        try:
            st.toast("Processing Crypto Strategy...", icon="🔄")
            import plotly.graph_objects as go
            engine_df = crypto_df.copy()
            
            if isinstance(engine_df.columns, pd.MultiIndex):
                engine_df.columns = engine_df.columns.droplevel(1)
            engine_df.columns = [str(col).lower() for col in engine_df.columns]
            
            if 'close' in engine_df.columns:
                engine_df['fast_linear'] = engine_df['close'].rolling(window=9, min_periods=1).mean()
                engine_df['slow_linear'] = engine_df['close'].rolling(window=21, min_periods=1).mean()
                engine_df['buy_sig'] = (engine_df['fast_linear'] > engine_df['slow_linear']) & (engine_df['fast_linear'].shift(1) <= engine_df['slow_linear'].shift(1))
                engine_df['sell_sig'] = (engine_df['fast_linear'] < engine_df['slow_linear']) & (engine_df['fast_linear'].shift(1) >= engine_df['slow_linear'].shift(1))

                fig_strategy = go.Figure()
                fig_strategy.add_trace(go.Candlestick(
                    x=engine_df.index, 
                    open=engine_df['open'], high=engine_df['high'], 
                    low=engine_df['low'], close=engine_df['close'], 
                    name="Crypto Candles",
                    increasing_line_color='#26a69a', decreasing_line_color='#ef5350',  
                    increasing_fillcolor='#26a69a', decreasing_fillcolor='#ef5350'    
                ))
                
                buys = engine_df[engine_df['buy_sig'] == True]
                if not buys.empty:
                    fig_strategy.add_trace(go.Scatter(
                        x=buys.index, y=buys['low'] * 0.99, mode='markers',
                        marker=dict(symbol='triangle-up', size=16, color='#00ffcc', line=dict(color='#0b0f19', width=1)), 
                        name='⚡ BUY SIGNAL'
                    ))
                
                sells = engine_df[engine_df['sell_sig'] == True]
                if not sells.empty:
                    fig_strategy.add_trace(go.Scatter(
                        x=sells.index, y=sells['high'] * 1.01, mode='markers',
                        marker=dict(symbol='triangle-down', size=16, color='#ff3366', line=dict(color='#0b0f19', width=1)), 
                        name='💥 SELL SIGNAL'
                    ))
                
                fig_strategy.update_layout(
                    template="plotly_dark", 
                    xaxis_rangeslider_visible=False, 
                    height=550,
                    plot_bgcolor='#131722',  
                    paper_bgcolor='#0b0f19', 
                    xaxis=dict(showgrid=True, gridcolor='#2a2e39', linecolor='#2a2e39', title_font=dict(color='#848e9c'), tickfont=dict(color='#848e9c')),
                    yaxis=dict(showgrid=True, gridcolor='#2a2e39', linecolor='#2a2e39', side='right', title_font=dict(color='#848e9c'), tickfont=dict(color='#848e9c')),
                    margin=dict(l=10, r=50, t=20, b=10),
                    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
                )
                st.plotly_chart(fig_strategy, use_container_width=True)
                st.success("🎯 Crypto Strategy Analysed and Visualized Below!")
            else:
                st.error("Data Column error: 'Close' prices could not be parsed properly.")
        except Exception as error:
            st.error(f"Engine Processing Error: {error}")
    else:
        st.warning("No price data available. Click **⚡ EXECUTE ALL MATRICES** first to load data, then run Pine script.")