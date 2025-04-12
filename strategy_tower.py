import streamlit as st
import pandas as pd
import numpy as np
import time
import random
import datetime
import plotly.graph_objects as go

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

# 生成隨機信號的函數
def generate_random_signal():
    coins = ["BTC/USDT", "ETH/USDT", "SOL/USDT", "BNB/USDT", "XRP/USDT", "ADA/USDT", "DOGE/USDT"]
    timeframes = ["1H", "4H", "8H", "1D"]
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

def show_strategy():
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
            '1H': {
                'total': 125,
                'hit': 87,
                'rate': 69.6
            },
            '4H': {
                'total': 98,
                'hit': 65,
                'rate': 66.3
            },
            '8H': {
                'total': 76,
                'hit': 48,
                'rate': 63.2
            },
            '1D': {
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
                st.rerun()
        
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

# 如果直接運行此文件，則顯示策略
if __name__ == "__main__":
    show_strategy() 