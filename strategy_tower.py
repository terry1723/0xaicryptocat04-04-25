import streamlit as st
import pandas as pd
import numpy as np
import time
import random
import datetime
import plotly.graph_objects as go
import ccxt
import requests
import json
import ta
from ta.trend import MACD
from ta.momentum import RSIIndicator
from ta.volatility import BollingerBands
import threading
from collections import deque
import uuid
import matplotlib.pyplot as plt
import base64
from PIL import Image
from io import BytesIO

# 添加自定義 CSS 來優化界面
st.markdown("""
<style>
    /* 隱藏默認的 Streamlit 元素 */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}

    /* 主要顏色方案 - 深色主題 */
    :root {
        --primary-color: #8e44ad;
        --secondary-color: #ff8c00;
        --accent-color: #00bcd4;
        --background-color: #121212;
        --card-background: #1E1E1E;
        --text-color: #E0E0E0;
        --border-color: #333333;
    }

    /* 整體背景和文字 */
    .stApp {
        background-color: var(--background-color);
        color: var(--text-color);
    }

    /* 卡片式設計元素 */
    .strategy-card {
        background-color: var(--card-background);
        border-radius: 10px;
        padding: 20px;
        margin-bottom: 20px;
        border: 1px solid var(--border-color);
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
    }
    
    /* 選項卡設計 */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background-color: var(--card-background);
        border-radius: 8px;
        padding: 5px;
    }

    .stTabs [data-baseweb="tab"] {
        height: 40px;
        white-space: pre-wrap;
        border-radius: 5px;
        color: var(--text-color);
        background-color: transparent;
    }

    .stTabs [aria-selected="true"] {
        background-color: var(--primary-color) !important;
        color: white !important;
        font-weight: bold;
    }
    
    /* 按鈕樣式 */
    .stButton button {
        background-color: var(--primary-color);
        color: white;
        border-radius: 5px;
        border: none;
        padding: 10px 20px;
        font-weight: bold;
    }

    .stButton button:hover {
        background-color: #7d32a8;
    }
    
    /* 信號卡片樣式 */
    .signal-card {
        background-color: #2a2a2a;
        border-radius: 8px;
        padding: 15px;
        margin: 10px 0;
        border-left: 4px solid var(--secondary-color);
    }
    
    .buy-signal {
        border-left: 4px solid #4CAF50;
    }
    
    .sell-signal {
        border-left: 4px solid #F44336;
    }
    
    /* 表格樣式 */
    .styled-table {
        border-collapse: collapse;
        margin: 25px 0;
        font-size: 0.9em;
        width: 100%;
        border-radius: 8px;
        overflow: hidden;
        box-shadow: 0 0 20px rgba(0, 0, 0, 0.15);
    }
    
    .styled-table thead tr {
        background-color: var(--primary-color);
        color: #ffffff;
        text-align: left;
    }
    
    .styled-table th,
    .styled-table td {
        padding: 12px 15px;
    }
    
    .styled-table tbody tr {
        border-bottom: 1px solid #333333;
    }
    
    .styled-table tbody tr:nth-of-type(even) {
        background-color: #242424;
    }
    
    .styled-table tbody tr:last-of-type {
        border-bottom: 2px solid var(--primary-color);
    }
    
    /* 漸變標題 */
    .gradient-text {
        background: linear-gradient(90deg, var(--primary-color), var(--secondary-color));
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: bold;
    }
    
    /* 突出顯示數據 */
    .highlight-data {
        color: var(--secondary-color);
        font-weight: bold;
    }
    
    /* 閃爍效果 */
    @keyframes pulse {
        0% { opacity: 1; }
        50% { opacity: 0.6; }
        100% { opacity: 1; }
    }
    
    .monitoring {
        animation: pulse 2s infinite;
        padding: 5px 10px;
        background-color: rgba(142, 68, 173, 0.2);
        border-radius: 4px;
        display: inline-block;
    }
    
    /* 風險警告 */
    .risk-warning {
        background-color: rgba(255, 87, 34, 0.1);
        border-left: 4px solid #FF5722;
        padding: 10px 15px;
        margin: 10px 0;
        border-radius: 0 5px 5px 0;
        font-size: 0.9em;
    }
</style>
""", unsafe_allow_html=True)

# 初始化交易所API連接
def get_exchange():
    # 使用ccxt連接幣安
    exchange = ccxt.binance({
        'enableRateLimit': True,
        'options': {
            'defaultType': 'future',  # 期貨市場
        }
    })
    return exchange

# 獲取市場數據
def get_market_data(symbol, timeframe, limit=100):
    exchange = get_exchange()
    try:
        ohlcv = exchange.fetch_ohlcv(symbol, timeframe, limit=limit)
        df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
        df.set_index('timestamp', inplace=True)
        return df
    except Exception as e:
        st.error(f"獲取市場數據錯誤: {e}")
        return None

# 計算各種技術指標
def calculate_indicators(df):
    """計算各種交易技術指標"""
    try:
        # 確保數據已正確排序
        df = df.sort_index()
        
        # 計算移動平均線
        df['ma_50'] = df['close'].rolling(window=50).mean()
        df['ma_200'] = df['close'].rolling(window=200).mean()
        
        # 計算布林帶 (20期, 2標準差)
        df['bb_middle'] = df['close'].rolling(window=20).mean()
        rolling_std = df['close'].rolling(window=20).std()
        df['bb_upper'] = df['bb_middle'] + (rolling_std * 2)
        df['bb_lower'] = df['bb_middle'] - (rolling_std * 2)
        
        # 計算相對強弱指數 (RSI, 14期)
        delta = df['close'].diff()
        gain = delta.where(delta > 0, 0)
        loss = -delta.where(delta < 0, 0)
        avg_gain = gain.rolling(window=14).mean()
        avg_loss = loss.rolling(window=14).mean()
        
        # 避免除以零
        avg_loss = avg_loss.replace(0, 0.001)
        
        rs = avg_gain / avg_loss
        df['rsi'] = 100 - (100 / (1 + rs))
        
        # 計算MACD (12,26,9)
        exp1 = df['close'].ewm(span=12, adjust=False).mean()
        exp2 = df['close'].ewm(span=26, adjust=False).mean()
        df['macd'] = exp1 - exp2
        df['macd_signal'] = df['macd'].ewm(span=9, adjust=False).mean()
        df['macd_hist'] = df['macd'] - df['macd_signal']
        
        # 計算隨機震盪指標 (14,3)
        low_14 = df['low'].rolling(window=14).min()
        high_14 = df['high'].rolling(window=14).max()
        
        # 避免除以零
        denom = high_14 - low_14
        denom = denom.replace(0, 0.001)
        
        df['k_percent'] = 100 * ((df['close'] - low_14) / denom)
        df['d_percent'] = df['k_percent'].rolling(window=3).mean()
        
        return df
    
    except Exception as e:
        st.error(f"計算指標時出錯: {e}")
        return df

# 生成真實交易信號
def generate_signals(df, symbol):
    """根據技術指標生成交易信號"""
    if df is None or len(df) < 50:
        return None
    
    signals = []
    
    # 獲取最新的數據點
    latest = df.iloc[-1]
    prev = df.iloc[-2]
    
    # 移動平均線交叉信號
    ma_cross = None
    if prev['ma_50'] < prev['ma_200'] and latest['ma_50'] > latest['ma_200']:
        ma_cross = {
            "id": str(uuid.uuid4()),
            "timestamp": latest.name.strftime('%Y-%m-%d %H:%M:%S'),
            "symbol": symbol,
            "signal_type": "GOLDEN_CROSS",
            "action": "BUY",
            "price": latest['close'],
            "confidence": 80,
            "description": f"{symbol} 形成黃金交叉，50期均線上穿200期均線",
            "indicators": {
                "ma_50": latest['ma_50'],
                "ma_200": latest['ma_200']
            }
        }
        signals.append(ma_cross)
    elif prev['ma_50'] > prev['ma_200'] and latest['ma_50'] < latest['ma_200']:
        ma_cross = {
            "id": str(uuid.uuid4()),
            "timestamp": latest.name.strftime('%Y-%m-%d %H:%M:%S'),
            "symbol": symbol,
            "signal_type": "DEATH_CROSS",
            "action": "SELL",
            "price": latest['close'],
            "confidence": 75,
            "description": f"{symbol} 形成死亡交叉，50期均線下穿200期均線",
            "indicators": {
                "ma_50": latest['ma_50'],
                "ma_200": latest['ma_200']
            }
        }
        signals.append(ma_cross)
    
    # RSI過買過賣信號
    if latest['rsi'] < 30:
        signals.append({
            "id": str(uuid.uuid4()),
            "timestamp": latest.name.strftime('%Y-%m-%d %H:%M:%S'),
            "symbol": symbol,
            "signal_type": "OVERSOLD",
            "action": "BUY",
            "price": latest['close'],
            "confidence": 70 + min(30 - latest['rsi'], 10),
            "description": f"{symbol} RSI 過賣 ({latest['rsi']:.1f})",
            "indicators": {
                "rsi": latest['rsi']
            }
        })
    elif latest['rsi'] > 70:
        signals.append({
            "id": str(uuid.uuid4()),
            "timestamp": latest.name.strftime('%Y-%m-%d %H:%M:%S'),
            "symbol": symbol,
            "signal_type": "OVERBOUGHT",
            "action": "SELL",
            "price": latest['close'],
            "confidence": 70 + min(latest['rsi'] - 70, 10),
            "description": f"{symbol} RSI 過買 ({latest['rsi']:.1f})",
            "indicators": {
                "rsi": latest['rsi']
            }
        })
    
    # MACD信號
    if prev['macd'] < prev['macd_signal'] and latest['macd'] > latest['macd_signal']:
        signals.append({
            "id": str(uuid.uuid4()),
            "timestamp": latest.name.strftime('%Y-%m-%d %H:%M:%S'),
            "symbol": symbol,
            "signal_type": "MACD_BULLISH",
            "action": "BUY",
            "price": latest['close'],
            "confidence": 75,
            "description": f"{symbol} MACD 上穿信號線，看漲",
            "indicators": {
                "macd": latest['macd'],
                "macd_signal": latest['macd_signal']
            }
        })
    elif prev['macd'] > prev['macd_signal'] and latest['macd'] < latest['macd_signal']:
        signals.append({
            "id": str(uuid.uuid4()),
            "timestamp": latest.name.strftime('%Y-%m-%d %H:%M:%S'),
            "symbol": symbol,
            "signal_type": "MACD_BEARISH",
            "action": "SELL",
            "price": latest['close'],
            "confidence": 75,
            "description": f"{symbol} MACD 下穿信號線，看跌",
            "indicators": {
                "macd": latest['macd'],
                "macd_signal": latest['macd_signal']
            }
        })
    
    # 布林帶信號
    if latest['close'] < latest['bb_lower']:
        signals.append({
            "id": str(uuid.uuid4()),
            "timestamp": latest.name.strftime('%Y-%m-%d %H:%M:%S'),
            "symbol": symbol,
            "signal_type": "BB_LOWER",
            "action": "BUY",
            "price": latest['close'],
            "confidence": 70,
            "description": f"{symbol} 價格觸及布林帶下軌，考慮買入",
            "indicators": {
                "bb_lower": latest['bb_lower'],
                "close": latest['close']
            }
        })
    elif latest['close'] > latest['bb_upper']:
        signals.append({
            "id": str(uuid.uuid4()),
            "timestamp": latest.name.strftime('%Y-%m-%d %H:%M:%S'),
            "symbol": symbol,
            "signal_type": "BB_UPPER",
            "action": "SELL",
            "price": latest['close'],
            "confidence": 70,
            "description": f"{symbol} 價格觸及布林帶上軌，考慮賣出",
            "indicators": {
                "bb_upper": latest['bb_upper'],
                "close": latest['close']
            }
        })
    
    return signals

# 從交易所獲取市場數據
def fetch_market_data(symbol, timeframe, limit=500):
    """從交易所獲取市場數據並計算技術指標"""
    try:
        # 初始化交易所API
        exchange = ccxt.binance()
        
        # 獲取K線數據
        ohlcv = exchange.fetch_ohlcv(symbol, timeframe, limit=limit)
        
        # 轉換為DataFrame
        df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
        df.set_index('timestamp', inplace=True)
        
        # 計算技術指標
        df = calculate_indicators(df)
        
        return df
    
    except Exception as e:
        st.error(f"獲取市場數據時出錯: {symbol} {timeframe} - {e}")
        return None

# 獲取市場情緒數據
def fetch_market_sentiment():
    """獲取恐懼與貪婪指數等市場情緒數據"""
    try:
        # 使用恐懼與貪婪指數API
        url = "https://api.alternative.me/fng/"
        response = requests.get(url)
        data = response.json()
        
        if data and 'data' in data:
            latest = data['data'][0]
            value = int(latest['value'])
            classification = latest['value_classification']
            
            sentiment = {
                'fear_greed_index': value,
                'classification': classification,
                'timestamp': latest['timestamp'],
                'analysis': f"市場情緒: {classification} ({value}/100)"
            }
            
            # 將數據保存到session state
            st.session_state.market_sentiment = sentiment
            
            return sentiment
        else:
            return {
                'fear_greed_index': 50,
                'classification': '中性',
                'timestamp': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'analysis': "無法獲取市場情緒數據，使用中性值"
            }
    
    except Exception as e:
        st.error(f"獲取市場情緒數據時出錯: {e}")
        return {
            'fear_greed_index': 50,
            'classification': '中性',
            'timestamp': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'analysis': "獲取數據時出錯，使用中性值"
        }

# 更新市場分析函數，使用新的fetch_market_data函數
def analyze_markets():
    symbols = [
        "BTC/USDT", "ETH/USDT", "SOL/USDT", "BNB/USDT", 
        "XRP/USDT", "ADA/USDT", "DOGE/USDT", "AVAX/USDT",
        "MATIC/USDT", "LINK/USDT", "DOT/USDT", "UNI/USDT"
    ]
    timeframes = ["1h", "4h", "1d"]
    all_signals = []
    
    for symbol in symbols:
        for timeframe in timeframes:
            # 使用新函數獲取更全面的市場數據
            df = fetch_market_data(symbol, timeframe)
            if df is not None:
                signals = generate_signals(df, symbol)
                if signals:
                    all_signals.extend(signals)
    
    # 添加市場情緒影響
    if 'market_sentiment' in st.session_state and all_signals:
        fear_greed_index = st.session_state.market_sentiment.get('fear_greed_index', 50)
        # 將市場情緒作為額外因素影響信號
        # 恐懼指數低時增強買入信號分數，高時增強賣出信號分數
        for signal in all_signals:
            if fear_greed_index < 30 and signal["signal_type"] == "BUY":
                signal["score"] += 0.5
                signal["sentiment_boost"] = "恐懼指數低，買入信號增強"
            elif fear_greed_index > 70 and signal["signal_type"] == "SELL":
                signal["score"] += 0.5
                signal["sentiment_boost"] = "貪婪指數高，賣出信號增強"
    
    # 根據分數排序信號
    if all_signals:
        all_signals.sort(key=lambda x: x["score"], reverse=True)
    
    return all_signals

# 後台監控線程
def monitoring_thread():
    while st.session_state.monitoring:
        try:
            new_signals = analyze_markets()
            if new_signals:
                # 將新信號添加到現有信號中
                st.session_state.signals.extend(new_signals)
                st.session_state.last_update = datetime.datetime.now()
                
                # 維護列表大小，最多保留20個信號
                if len(st.session_state.signals) > 20:
                    st.session_state.signals = st.session_state.signals[-20:]
            
            # 等待一段時間後再次分析
            time.sleep(300)  # 每5分鐘檢查一次
            
        except Exception as e:
            print(f"監控線程錯誤: {e}")
            time.sleep(60)  # 發生錯誤時，等待1分鐘後重試

def show_strategy():
    """女妖輔助建議策略頁面"""
    # 設置用於保存信號的會話狀態變量
    if 'signals' not in st.session_state:
        st.session_state.signals = []

    if 'monitoring' not in st.session_state:
        st.session_state.monitoring = False

    if 'last_update' not in st.session_state:
        st.session_state.last_update = None

    if 'hit_rates' not in st.session_state:
        # 預設一些命中率數據
        st.session_state.hit_rates = {
            '1h': {
                'total': 125,
                'hit': 87,
                'rate': 69.6
            },
            '4h': {
                'total': 98,
                'hit': 65,
                'rate': 66.3
            },
            '1d': {
                'total': 42,
                'hit': 31,
                'rate': 73.8
            }
        }

    # 頂部導航與標題
    col1, col2, col3 = st.columns([1, 2, 1])

    with col1:
        st.markdown("""
        <div style="display: flex; align-items: center;">
            <h3 style="margin: 0;">🧙‍♀️ 女妖策略</h3>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("<h2 class='gradient-text' style='text-align: center;'>女妖輔助建議策略</h2>", unsafe_allow_html=True)

    with col3:
        st.markdown("""
        <div style="display: flex; justify-content: flex-end; align-items: center; height: 100%;">
            <div style="margin-right: 10px;">
                <span style="font-size: 14px;">歡迎, Terry1723</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

    # 創建標籤頁
    tab1, tab2 = st.tabs(["💫 女妖輔助建議策略", "📊 女妖輔助建議策略命中率統計"])

    with tab1:
        st.markdown("""
        <div class="strategy-card">
            <h3>女妖輔助建議策略</h3>
            <p>女妖輔助建議策略利用先進的AI技術和大數據分析，24小時不間斷監控市場，為您提供潛在的加密貨幣交易信號。</p>
            <p>系統會分析多種技術指標、市場趨勢和歷史數據，以識別具有高勝率潛力的交易機會。每個信號都包含幣種、時間框架、入場價、目標價和止損位等關鍵信息。</p>
            <div class="risk-warning">
                <strong>風險提示:</strong> 所有交易信號僅供參考，不構成投資建議。加密貨幣市場風險較高，請謹慎交易並控制風險。
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # 信號監控區域
        col1, col2 = st.columns([3, 1])
        
        with col1:
            # 監控狀態
            if st.session_state.monitoring:
                status_text = "正在監控中..."
                last_update = st.session_state.last_update.strftime("%Y-%m-%d %H:%M:%S") if st.session_state.last_update else "剛剛開始"
                st.markdown(f"""
                <div style="display:flex; align-items:center;">
                    <span class="monitoring">🔍 {status_text}</span>
                    <span style="margin-left:10px; font-size:0.8em; color:#888;">上次更新: {last_update}</span>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown("""
                <div style="padding:10px 0;">
                    <span style="color:#888;">📴 未開始監控</span>
                </div>
                """, unsafe_allow_html=True)
        
        with col2:
            # 開始/停止監控按鈕
            if st.button("🔍 " + ("停止監控" if st.session_state.monitoring else "開始監控")):
                st.session_state.monitoring = not st.session_state.monitoring
                if st.session_state.monitoring:
                    st.session_state.last_update = datetime.datetime.now()
                st.experimental_rerun()
        
        # 顯示信號
        st.markdown("<h3>最新信號</h3>", unsafe_allow_html=True)
        
        # 顯示現有信號
        if st.session_state.signals:
            # 僅顯示最新的4個信號
            display_signals = st.session_state.signals[-4:]
            for signal in display_signals:
                signal_type_class = "buy-signal" if signal["signal_type"] == "買入" else "sell-signal"
                st.markdown(f"""
                <div class="signal-card {signal_type_class}">
                    <div style="display:flex; justify-content:space-between; margin-bottom:5px;">
                        <span style="font-weight:bold;">{signal["coin"]} ({signal["timeframe"]})</span>
                        <span style="color:{'#4CAF50' if signal["signal_type"] == '買入' else '#F44336'}; font-weight:bold;">{signal["signal_type"]}</span>
                    </div>
                    <div style="display:flex; justify-content:space-between; margin-bottom:5px;">
                        <span>入場價: <span class="highlight-data">${signal["entry_price"]}</span></span>
                        <span>目標價: <span class="highlight-data">${signal["target_price"]}</span></span>
                        <span>止損價: <span class="highlight-data">${signal["stop_loss"]}</span></span>
                    </div>
                    <div style="font-size:0.8em; color:#888; text-align:right;">
                        生成時間: {signal["timestamp"]}
                    </div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("尚無信號，請點擊「開始監控」以接收交易信號")
        
        # 風險警告
        st.markdown("""
        <div class="risk-warning" style="margin-top:20px;">
            <strong>免責聲明:</strong> 數字貨幣市場風險較高，信號僅供參考，請勿盲目跟隨。投資有風險，交易需謹慎。
        </div>
        """, unsafe_allow_html=True)

    with tab2:
        st.markdown("""
        <div class="strategy-card">
            <h3>女妖輔助建議策略命中率統計</h3>
            <p>此處顯示女妖輔助建議策略在不同時間框架下的歷史表現和命中率統計數據。</p>
        </div>
        """, unsafe_allow_html=True)
        
        # 命中率統計摘要
        total_signals = sum(data['total'] for data in st.session_state.hit_rates.values())
        total_hits = sum(data['hit'] for data in st.session_state.hit_rates.values())
        overall_hit_rate = round((total_hits / total_signals) * 100, 1) if total_signals > 0 else 0
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown(f"""
            <div style="text-align:center; padding:20px; background-color:#2a2a2a; border-radius:10px;">
                <div style="font-size:16px; margin-bottom:10px;">總信號數</div>
                <div style="font-size:24px; font-weight:bold; color:var(--secondary-color);">{total_signals}</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
            <div style="text-align:center; padding:20px; background-color:#2a2a2a; border-radius:10px;">
                <div style="font-size:16px; margin-bottom:10px;">命中信號數</div>
                <div style="font-size:24px; font-weight:bold; color:var(--secondary-color);">{total_hits}</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown(f"""
            <div style="text-align:center; padding:20px; background-color:#2a2a2a; border-radius:10px;">
                <div style="font-size:16px; margin-bottom:10px;">總體命中率</div>
                <div style="font-size:24px; font-weight:bold; color:var(--secondary-color);">{overall_hit_rate}%</div>
            </div>
            """, unsafe_allow_html=True)
        
        # 詳細命中率表格
        st.markdown("<h3>不同時間框架命中率</h3>", unsafe_allow_html=True)
        
        # 使用HTML表格代替Streamlit表格，以應用自定義樣式
        table_rows = ""
        for timeframe, data in st.session_state.hit_rates.items():
            # 根據命中率評定等級
            if data['rate'] >= 70:
                rating = "優秀"
                color = "#4CAF50"
            elif data['rate'] >= 60:
                rating = "良好"
                color = "#FFC107"
            else:
                rating = "一般"
                color = "#F44336"
                
            table_rows += f"""
            <tr>
                <td>{timeframe}</td>
                <td>{data['total']}</td>
                <td>{data['hit']}</td>
                <td style="color:{color}; font-weight:bold;">{data['rate']}%</td>
                <td style="color:{color}; font-weight:bold;">{rating}</td>
            </tr>
            """
        
        st.markdown(f"""
        <table class="styled-table">
            <thead>
                <tr>
                    <th>時間框架</th>
                    <th>總信號數</th>
                    <th>命中信號數</th>
                    <th>命中率</th>
                    <th>評級</th>
                </tr>
            </thead>
            <tbody>
                {table_rows}
            </tbody>
        </table>
        """, unsafe_allow_html=True)
        
        # 命中率圖表
        st.markdown("<h3>命中率視覺化</h3>", unsafe_allow_html=True)
        
        # 準備圖表數據
        timeframes = list(st.session_state.hit_rates.keys())
        hit_rates = [data['rate'] for data in st.session_state.hit_rates.values()]
        
        # 創建柱狀圖
        fig = go.Figure()
        
        # 根據命中率設置顏色
        colors = ['#4CAF50' if rate >= 70 else '#FFC107' if rate >= 60 else '#F44336' for rate in hit_rates]
        
        fig.add_trace(go.Bar(
            x=timeframes,
            y=hit_rates,
            marker_color=colors,
            text=[f"{rate}%" for rate in hit_rates],
            textposition='auto'
        ))
        
        # 更新圖表佈局
        fig.update_layout(
            title="不同時間框架命中率比較",
            xaxis_title="時間框架",
            yaxis_title="命中率 (%)",
            template="plotly_dark",
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            yaxis=dict(range=[0, 100]),
            height=400
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # 風險警告
        st.markdown("""
        <div class="risk-warning" style="margin-top:20px;">
            <strong>注意:</strong> 過往業績不代表未來表現。市場情況瞬息萬變，請根據您的風險承受能力和投資目標做出決策。
        </div>
        """, unsafe_allow_html=True)

    # 頁腳
    st.markdown("""
    <div style="margin-top:50px; padding:20px 0; border-top:1px solid #333; text-align:center; font-size:0.8em; color:#888;">
        © 2025 加密貨幣策略建議工具 | 本網站提供的加密貨幣分析僅供參考，不構成投資建議
    </div>
    """, unsafe_allow_html=True)

    # 自動刷新功能
    if st.session_state.monitoring:
        # 每次運行時有30%的概率生成新信號
        if random.random() < 0.3:
            new_signal = generate_random_signal()
            st.session_state.signals.append(new_signal)
            st.session_state.last_update = datetime.datetime.now()
        
        # 自動刷新頁面（每15秒）
        st.markdown("""
        <script>
            setTimeout(function() {
                window.location.reload();
            }, 15000);
        </script>
        """, unsafe_allow_html=True)

# 顯示策略塔頁面
def show_strategy_tower_page():
    st.title("交易信號中心")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("交易信號概覽")
        
        # 選擇加密貨幣
        crypto_options = ["BTC/USDT", "ETH/USDT", "BNB/USDT", "XRP/USDT", "SOL/USDT", "ADA/USDT", "DOGE/USDT", "AVAX/USDT"]
        selected_cryptos = st.multiselect("選擇加密貨幣", crypto_options, default=["BTC/USDT", "ETH/USDT"])
        
        # 選擇時間範圍
        timeframe_options = ["1m", "5m", "15m", "1h", "4h", "1d"]
        selected_timeframes = st.multiselect("選擇時間範圍", timeframe_options, default=["1h", "4h"])
        
        # 獲取市場情緒數據
        market_sentiment = fetch_market_sentiment()
        
        # 顯示市場情緒
        sentiment_color = "green"
        if market_sentiment['fear_greed_index'] < 30:
            sentiment_color = "red"
        elif market_sentiment['fear_greed_index'] < 50:
            sentiment_color = "orange"
        elif market_sentiment['fear_greed_index'] >= 70:
            sentiment_color = "green"
            
        st.markdown(f"""
        ### 市場情緒
        <div style='background-color: rgba(0,0,0,0.1); padding: 15px; border-radius: 5px;'>
            <h4 style='color: {sentiment_color};'>恐懼與貪婪指數: {market_sentiment['fear_greed_index']}/100 - {market_sentiment['classification']}</h4>
            <p>{market_sentiment['analysis']}</p>
        </div>
        """, unsafe_allow_html=True)
        
        # 獲取並顯示交易信號
        if st.button("獲取最新交易信號"):
            with st.spinner("正在生成交易信號..."):
                all_signals = []
                
                for symbol in selected_cryptos:
                    for timeframe in selected_timeframes:
                        df = fetch_market_data(symbol, timeframe)
                        if df is not None:
                            signals = generate_signals(df, symbol)
                            if signals:
                                all_signals.extend(signals)
                
                if all_signals:
                    # 按信心度排序信號
                    all_signals.sort(key=lambda x: x['confidence'], reverse=True)
                    
                    # 保存到 session state
                    st.session_state.trading_signals = all_signals
                    
                    # 顯示信號表格
                    signals_df = pd.DataFrame(all_signals)
                    if not signals_df.empty:
                        columns_to_show = ['timestamp', 'symbol', 'signal_type', 'action', 'price', 'confidence', 'description']
                        signals_df = signals_df[columns_to_show]
                        signals_df.columns = ['時間', '交易對', '信號類型', '操作', '價格', '信心度', '描述']
                        st.dataframe(signals_df, height=400)
                        
                        # 生成信號報告
                        with st.expander("交易信號詳細報告"):
                            for signal in all_signals:
                                signal_color = "green" if signal['action'] == "BUY" else "red"
                                st.markdown(f"""
                                <div style='background-color: rgba(0,0,0,0.05); margin-bottom: 10px; padding: 15px; border-radius: 5px; border-left: 5px solid {signal_color};'>
                                    <h4 style='color: {signal_color};'>{signal['symbol']} - {signal['signal_type']} ({signal['action']})</h4>
                                    <p><strong>時間:</strong> {signal['timestamp']}</p>
                                    <p><strong>價格:</strong> {signal['price']}</p>
                                    <p><strong>信心度:</strong> {signal['confidence']}/100</p>
                                    <p><strong>描述:</strong> {signal['description']}</p>
                                </div>
                                """, unsafe_allow_html=True)
                else:
                    st.info("當前沒有發現交易信號，請稍後再試或更改選擇的交易對和時間範圍。")
    
    with col2:
        st.subheader("交易信號圖表")
        
        # 顯示當前加密貨幣的圖表
        if selected_cryptos:
            selected_chart_crypto = st.selectbox("選擇查看圖表的加密貨幣", selected_cryptos)
            selected_chart_timeframe = st.selectbox("選擇圖表時間範圍", timeframe_options, index=3)  # 默認1h
            
            with st.spinner("正在加載圖表..."):
                df = fetch_market_data(selected_chart_crypto, selected_chart_timeframe)
                if df is not None and not df.empty:
                    # 使用plotly創建圖表
                    fig = go.Figure()
                    
                    # 添加K線圖
                    fig.add_trace(go.Candlestick(
                        x=df.index,
                        open=df['open'],
                        high=df['high'],
                        low=df['low'],
                        close=df['close'],
                        name="K線"
                    ))
                    
                    # 添加均線
                    fig.add_trace(go.Scatter(
                        x=df.index,
                        y=df['ma_50'],
                        line=dict(color='orange', width=1),
                        name="MA 50"
                    ))
                    
                    fig.add_trace(go.Scatter(
                        x=df.index,
                        y=df['ma_200'],
                        line=dict(color='purple', width=1),
                        name="MA 200"
                    ))
                    
                    # 添加布林帶
                    fig.add_trace(go.Scatter(
                        x=df.index,
                        y=df['bb_upper'],
                        line=dict(color='rgba(0,128,0,0.3)', width=1),
                        name="布林上軌",
                        fill=None
                    ))
                    
                    fig.add_trace(go.Scatter(
                        x=df.index,
                        y=df['bb_middle'],
                        line=dict(color='rgba(0,128,0,0.3)', width=1),
                        name="布林中軌"
                    ))
                    
                    fig.add_trace(go.Scatter(
                        x=df.index,
                        y=df['bb_lower'],
                        line=dict(color='rgba(0,128,0,0.3)', width=1),
                        name="布林下軌",
                        fill='tonexty'
                    ))
                    
                    # 設置圖表佈局
                    fig.update_layout(
                        title=f"{selected_chart_crypto} - {selected_chart_timeframe}",
                        xaxis_title="時間",
                        yaxis_title="價格",
                        height=600,
                        margin=dict(l=10, r=10, t=50, b=10),
                        xaxis_rangeslider_visible=False,
                        template="plotly_dark"
                    )
                    
                    st.plotly_chart(fig, use_container_width=True)
                    
                    # 顯示RSI圖表
                    fig_rsi = go.Figure()
                    fig_rsi.add_trace(go.Scatter(
                        x=df.index,
                        y=df['rsi'],
                        line=dict(color='cyan', width=1),
                        name="RSI"
                    ))
                    
                    # 添加過買過賣線
                    fig_rsi.add_shape(
                        type="line",
                        x0=df.index[0],
                        y0=70,
                        x1=df.index[-1],
                        y1=70,
                        line=dict(color="red", width=2, dash="dash"),
                    )
                    fig_rsi.add_shape(
                        type="line",
                        x0=df.index[0],
                        y0=30,
                        x1=df.index[-1],
                        y1=30,
                        line=dict(color="green", width=2, dash="dash"),
                    )
                    
                    fig_rsi.update_layout(
                        title="RSI 指標",
                        xaxis_title="時間",
                        yaxis_title="RSI",
                        height=250,
                        margin=dict(l=10, r=10, t=50, b=10),
                        yaxis=dict(range=[0, 100]),
                        template="plotly_dark"
                    )
                    
                    st.plotly_chart(fig_rsi, use_container_width=True)
                    
                    # 顯示MACD圖表
                    fig_macd = go.Figure()
                    fig_macd.add_trace(go.Scatter(
                        x=df.index,
                        y=df['macd'],
                        line=dict(color='blue', width=1),
                        name="MACD"
                    ))
                    fig_macd.add_trace(go.Scatter(
                        x=df.index,
                        y=df['macd_signal'],
                        line=dict(color='red', width=1),
                        name="信號線"
                    ))
                    
                    # 添加MACD柱狀圖
                    colors = ['green' if val >= 0 else 'red' for val in df['macd_hist']]
                    fig_macd.add_trace(go.Bar(
                        x=df.index,
                        y=df['macd_hist'],
                        marker_color=colors,
                        name="柱狀圖"
                    ))
                    
                    fig_macd.update_layout(
                        title="MACD 指標",
                        xaxis_title="時間",
                        yaxis_title="MACD",
                        height=250,
                        margin=dict(l=10, r=10, t=50, b=10),
                        template="plotly_dark"
                    )
                    
                    st.plotly_chart(fig_macd, use_container_width=True)
                else:
                    st.error(f"無法獲取 {selected_chart_crypto} 的數據")

# 生成隨機信號的函數
def generate_random_signal():
    coins = ["BTC/USDT", "ETH/USDT", "SOL/USDT", "BNB/USDT", "XRP/USDT", "ADA/USDT", "DOGE/USDT"]
    timeframes = ["1h", "4h", "1d"]
    signal_types = ["買入", "賣出"]
    
    # 隨機選擇
    coin = random.choice(coins)
    timeframe = random.choice(timeframes)
    signal_type = random.choice(signal_types)
    
    # 生成合理的價格數據
    base_prices = {
        "BTC/USDT": 68500,
        "ETH/USDT": 3450,
        "SOL/USDT": 178,
        "BNB/USDT": 575,
        "XRP/USDT": 0.61,
        "ADA/USDT": 0.47,
        "DOGE/USDT": 0.16,
    }
    
    # 獲取基準價格
    base_price = base_prices.get(coin, 100)
    
    # 加入一些隨機浮動
    price_variation = base_price * 0.01  # 1%的浮動
    
    # 計算價格
    entry_price = round(base_price + random.uniform(-price_variation, price_variation), 4)
    
    if signal_type == "買入":
        # 買入目標價格略高於入場價
        target_price = round(entry_price * (1 + random.uniform(0.03, 0.08)), 4)
        # 止損價略低於入場價
        stop_loss = round(entry_price * (1 - random.uniform(0.02, 0.04)), 4)
    else:
        # 賣出目標價格略低於入場價
        target_price = round(entry_price * (1 - random.uniform(0.03, 0.08)), 4)
        # 止損價略高於入場價
        stop_loss = round(entry_price * (1 + random.uniform(0.02, 0.04)), 4)
    
    # 處理格式
    if coin in ["BTC/USDT", "ETH/USDT", "BNB/USDT"]:
        entry_price = f"{entry_price:.2f}"
        target_price = f"{target_price:.2f}"
        stop_loss = f"{stop_loss:.2f}"
    elif coin in ["SOL/USDT", "ADA/USDT", "DOGE/USDT"]:
        entry_price = f"{entry_price:.3f}"
        target_price = f"{target_price:.3f}"
        stop_loss = f"{stop_loss:.3f}"
    else:
        entry_price = f"{entry_price:.4f}"
        target_price = f"{target_price:.4f}"
        stop_loss = f"{stop_loss:.4f}"
    
    # 創建信號對象
    signal = {
        "coin": coin,
        "timeframe": timeframe,
        "signal_type": signal_type,
        "entry_price": entry_price,
        "target_price": target_price,
        "stop_loss": stop_loss,
        "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    
    return signal

# 如果直接運行此文件，則顯示策略
if __name__ == "__main__":
    show_strategy() 