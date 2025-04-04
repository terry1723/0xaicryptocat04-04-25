import streamlit as st
import pandas as pd
import numpy as np
import ccxt
import time
import random
from datetime import datetime, timedelta
import plotly.graph_objects as go
import requests
import json
import os

# 設置頁面配置
st.set_page_config(
    page_title="0xAI CryptoCat 分析",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# 添加自定義 CSS 來優化界面
st.markdown("""
<style>
    /* 隱藏側邊欄以及默認的 Streamlit 元素 */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}

    /* 主要顏色方案 - 深色主題 */
    :root {
        --primary-color: #4a8af4;
        --secondary-color: #9C27B0;
        --accent-color: #00BCD4;
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
    .stCardContainer {
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
        background-color: #3A7AD5;
    }

    /* 展開/摺疊元素樣式 */
    .streamlit-expanderHeader {
        background-color: var(--card-background);
        border-radius: 8px;
        color: var(--text-color);
        font-weight: 500;
    }

    /* 數據表格樣式 */
    .dataframe {
        border-radius: 8px;
        overflow: hidden;
    }

    /* 頂部導航欄 */
    .nav-container {
        background-color: var(--card-background);
        padding: 10px;
        border-radius: 10px;
        margin-bottom: 20px;
        display: flex;
        justify-content: space-between;
        align-items: center;
        border: 1px solid var(--border-color);
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
    }

    /* 進度指示器 */
    .stProgress > div > div {
        background-color: var(--primary-color);
    }

    /* 提示條樣式 */
    .stAlert {
        border-radius: 8px;
    }

    /* 醒目數據展示 */
    .highlight-metric {
        background-color: var(--card-background);
        border-left: 4px solid var(--primary-color);
        padding: 10px 15px;
        margin: 5px 0;
        border-radius: 0 5px 5px 0;
    }
    
    /* 標題樣式 */
    h1, h2, h3 {
        color: var(--primary-color);
    }
    
    /* 自定義卡片 */
    .data-card {
        background-color: var(--card-background);
        border-radius: 8px;
        padding: 15px;
        box-shadow: 0 2px 5px rgba(0,0,0,0.2);
        margin-bottom: 15px;
    }
    
    /* 重要數據顯示 */
    .key-metric {
        font-size: 24px;
        font-weight: bold;
        color: var(--accent-color);
    }
    
    /* 分析結果摘要區 */
    .analysis-summary {
        background-color: rgba(74, 138, 244, 0.1);
        border-radius: 8px;
        padding: 15px;
        margin: 10px 0;
        border-left: 4px solid var(--primary-color);
    }
</style>
""", unsafe_allow_html=True)

# 處理 orjson 相關問題
import plotly.io._json
# 如果 orjson 存在，修復 OPT_NON_STR_KEYS 問題
try:
    import orjson
    if not hasattr(orjson, 'OPT_NON_STR_KEYS'):
        orjson.OPT_NON_STR_KEYS = 2  # 定義缺失的常量
except ImportError:
    pass
except AttributeError:
    # 修改 _json_to_plotly 方法，避免使用 OPT_NON_STR_KEYS
    orig_to_json_plotly = plotly.io._json.to_json_plotly
    def patched_to_json_plotly(fig_dict, *args, **kwargs):
        try:
            return orig_to_json_plotly(fig_dict, *args, **kwargs)
        except AttributeError:
            # 使用 json 而不是 orjson 進行序列化
            return json.dumps(fig_dict)
    plotly.io._json.to_json_plotly = patched_to_json_plotly

# 安全地從 secrets 或環境變量獲取 API 密鑰
def get_api_key(key_name, default_value=None):
    """安全地獲取 API 密鑰，優先從 Streamlit secrets 獲取，然後是環境變量，最後是默認值"""
    try:
        if key_name in st.secrets:
            return st.secrets[key_name]
    except Exception:
        # 忽略 secrets 相關錯誤
        pass
        
    # 如果無法從 secrets 獲取，嘗試從環境變量獲取，最後使用默認值
    return os.getenv(key_name, default_value)

# 從Streamlit secrets或環境變數讀取API密鑰，如果都不存在則使用預設值
DEEPSEEK_API_KEY = get_api_key("DEEPSEEK_API_KEY", "sk-6ae04d6789f94178b4053d2c42650b6c")

# 設置 CoinMarketCap API 密鑰
COINMARKETCAP_API_KEY = get_api_key("COINMARKETCAP_API_KEY", "b54bcf4d-1bca-4e8e-9a24-22ff2c3d462c")

# 新增：設置 OpenAI API 密鑰
OPENAI_API_KEY = get_api_key("OPENAI_API_KEY", "")

# 設置 Bitget MCP 服務器
BITGET_MCP_SERVER = "http://localhost:3000"

# 保留原有的數據獲取和分析函數...
# 這裡省略大量代碼，保持原有功能不變
# ...

# 應用標題和導航 - 使用列布局替代側邊欄
st.markdown("""
<div style="text-align: center; padding: 20px 0;">
    <h1>0xAI CryptoCat 加密貨幣分析儀表板</h1>
    <p>多模型AI驅動的加密貨幣技術與市場情緒分析</p>
</div>
""", unsafe_allow_html=True)

# 頂部導航欄 - 使用tab切換不同功能
tabs = st.tabs(["📈 技術分析", "🧠 AI 分析", "📊 市場數據", "⚙️ 設置"])

with tabs[0]:
    # 技術分析標籤內容
    st.markdown("<h2>技術分析儀表板</h2>", unsafe_allow_html=True)
    
    # 使用列布局安排控制元素
    col1, col2, col3, col4 = st.columns([2, 2, 2, 1])
    
    with col1:
        # 使用下拉菜單而非側邊欄選項
        coin_options = {
            'BTC/USDT': '比特幣 (BTC)',
            'ETH/USDT': '以太坊 (ETH)',
            'SOL/USDT': '索拉納 (SOL)',
            'BNB/USDT': '幣安幣 (BNB)',
            'XRP/USDT': '瑞波幣 (XRP)',
            'ADA/USDT': '艾達幣 (ADA)',
            'DOGE/USDT': '狗狗幣 (DOGE)',
            'SHIB/USDT': '柴犬幣 (SHIB)'
        }
        selected_symbol = st.selectbox('選擇加密貨幣', list(coin_options.keys()), format_func=lambda x: coin_options[x])
    
    with col2:
        timeframe_options = {
            '15m': '15分鐘',
            '1h': '1小時',
            '4h': '4小時',
            '1d': '1天',
            '1w': '1週'
        }
        selected_timeframe = st.selectbox('選擇時間框架', list(timeframe_options.keys()), format_func=lambda x: timeframe_options[x])
    
    with col3:
        # 額外選項，例如交易量顯示、指標選擇等
        show_volume = st.checkbox('顯示交易量', value=True)
        
    with col4:
        # 分析按鈕
        st.markdown("<br>", unsafe_allow_html=True)  # 添加一些空間來對齊按鈕
        analyze_button = st.button('開始分析', use_container_width=True)
    
    # 使用卡片式設計展示主要圖表
    st.markdown('<div class="stCardContainer">', unsafe_allow_html=True)
    
    # 這裡放置主要價格圖表
    # 您可以保留原有的圖表生成代碼，但將其放在這個卡片容器中
    
    # 模擬價格圖表
    if 'analyzed' not in st.session_state:
        st.session_state.analyzed = False
        
    if analyze_button or st.session_state.analyzed:
        st.session_state.analyzed = True
        
        # 顯示加載中動畫
        with st.spinner(f"正在獲取 {selected_symbol} 數據並進行分析..."):
            # 使用DexScreener API獲取真實數據
            df = get_crypto_data(selected_symbol, selected_timeframe, limit=100)
            
            if df is not None:
                # 使用真實數據創建圖表
                fig = go.Figure()
                
                # 添加蠟燭圖 - 使用實際數據
                fig.add_trace(go.Candlestick(
                    x=df['timestamp'],
                    open=df['open'],
                    high=df['high'],
                    low=df['low'],
                    close=df['close'],
                    name='價格'
                ))
                
                # 計算移動平均線
                df['ma20'] = df['close'].rolling(window=20).mean()
                df['ma50'] = df['close'].rolling(window=50).mean()
                
                # 添加移動平均線 - 使用實際數據
                fig.add_trace(go.Scatter(
                    x=df['timestamp'],
                    y=df['ma20'],
                    mode='lines',
                    name='MA20',
                    line=dict(color='#9C27B0', width=2)
                ))
                
                fig.add_trace(go.Scatter(
                    x=df['timestamp'],
                    y=df['ma50'],
                    mode='lines',
                    name='MA50',
                    line=dict(color='#00BCD4', width=2)
                ))
                
                # 更新布局
                fig.update_layout(
                    title=f'{selected_symbol} 價格圖表 ({selected_timeframe})',
                    xaxis_title='日期',
                    yaxis_title='價格 (USDT)',
                    template='plotly_dark',
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    xaxis=dict(showgrid=False),
                    yaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.1)'),
                    height=500,
                    margin=dict(l=40, r=40, t=60, b=40)
                )
                
                # 顯示圖表
                st.plotly_chart(fig, use_container_width=True)
                
                if show_volume:
                    # 添加成交量圖表 - 使用實際數據
                    volume_fig = go.Figure()
                    volume_fig.add_trace(go.Bar(
                        x=df['timestamp'],
                        y=df['volume'],
                        marker_color='rgba(74, 138, 244, 0.7)',
                        name='成交量'
                    ))
                    
                    volume_fig.update_layout(
                        title='交易量',
                        xaxis_title='日期',
                        yaxis_title='成交量',
                        template='plotly_dark',
                        plot_bgcolor='rgba(0,0,0,0)',
                        paper_bgcolor='rgba(0,0,0,0)',
                        xaxis=dict(showgrid=False),
                        yaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.1)'),
                        height=250,
                        margin=dict(l=40, r=40, t=40, b=40)
                    )
                    
                    st.plotly_chart(volume_fig, use_container_width=True)
                
                # 進行真實技術分析
                smc_data = smc_analysis(df)
                snr_data = snr_analysis(df)
            else:
                st.error(f"無法獲取 {selected_symbol} 的數據，請稍後再試或選擇其他幣種。")
    else:
        # 顯示占位符提示
        st.info("請選擇加密貨幣和時間框架，然後點擊「開始分析」按鈕來查看技術分析。")
        
    st.markdown('</div>', unsafe_allow_html=True)
    
    # 使用可折疊區域顯示更多指標和詳細信息
    if st.session_state.get('analyzed', False):
        # 使用兩列布局顯示關鍵指標
        col1, col2 = st.columns(2)
        
        with col1:
            # SMC 分析結果卡片
            st.markdown('<div class="stCardContainer">', unsafe_allow_html=True)
            st.markdown("<h3>SMC 市場結構分析</h3>", unsafe_allow_html=True)
            
            # 使用真實SMC分析數據
            # 顯示主要信息
            st.markdown(f"""
            <div class="highlight-metric">市場結構: {"看漲" if smc_data["market_structure"] == "bullish" else "看跌"}</div>
            <div class="highlight-metric">趨勢強度: {smc_data["trend_strength"]:.2f}</div>
            <div class="highlight-metric">當前價格: ${smc_data["price"]:.2f}</div>
            """, unsafe_allow_html=True)
            
            # 使用可折疊部分顯示更多細節
            with st.expander("查看詳細 SMC 分析"):
                st.markdown(f"""
                **支撐位**: ${smc_data["support_level"]:.2f}  
                **阻力位**: ${smc_data["resistance_level"]:.2f}  
                **SMC 建議**: {"買入" if smc_data["recommendation"] == "buy" else "賣出" if smc_data["recommendation"] == "sell" else "觀望"}
                
                **重要價格水平**:
                - 當前價格: ${smc_data["price"]:.2f}
                - 關鍵支撐: ${smc_data["key_support"]:.2f}
                - 關鍵阻力: ${smc_data["key_resistance"]:.2f}
                
                **趨勢信息**:
                - 市場結構: {"看漲" if smc_data["market_structure"] == "bullish" else "看跌"}
                - 趨勢強度: {smc_data["trend_strength"]:.2f}
                - 趨勢持續性: {"高" if smc_data["trend_strength"] > 0.7 else "中等" if smc_data["trend_strength"] > 0.4 else "低"}
                """)
                
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col2:
            # SNR 分析結果卡片
            st.markdown('<div class="stCardContainer">', unsafe_allow_html=True)
            st.markdown("<h3>SNR 供需分析</h3>", unsafe_allow_html=True)
            
            # 使用真實SNR分析數據
            # 顯示主要信息
            rsi_state = "超買" if snr_data["overbought"] else "超賣" if snr_data["oversold"] else "中性"
            st.markdown(f"""
            <div class="highlight-metric">RSI: {snr_data["rsi"]:.2f} ({rsi_state})</div>
            <div class="highlight-metric">近期支撐位: ${snr_data["near_support"]:.2f}</div>
            <div class="highlight-metric">近期阻力位: ${snr_data["near_resistance"]:.2f}</div>
            """, unsafe_allow_html=True)
            
            # 使用可折疊部分顯示更多細節
            with st.expander("查看詳細 SNR 分析"):
                st.markdown(f"""
                **強支撐位**: ${snr_data["strong_support"]:.2f}  
                **強阻力位**: ${snr_data["strong_resistance"]:.2f}  
                **SNR 建議**: {"買入" if snr_data["recommendation"] == "buy" else "賣出" if snr_data["recommendation"] == "sell" else "觀望"}
                
                **技術指標**:
                - RSI ({selected_timeframe}): {snr_data["rsi"]:.2f}
                - 狀態: {"超買" if snr_data["overbought"] else "超賣" if snr_data["oversold"] else "中性"}
                - 動能方向: {"上升" if snr_data.get("momentum_up", False) else "下降" if snr_data.get("momentum_down", False) else "中性"}
                
                **供需區域**:
                - 主要供應區: ${snr_data["strong_resistance"]:.2f} 到 ${snr_data["near_resistance"]:.2f}
                - 主要需求區: ${snr_data["near_support"]:.2f} 到 ${snr_data["strong_support"]:.2f}
                """)
                
            st.markdown('</div>', unsafe_allow_html=True)
        
        # 綜合分析結果區域
        st.markdown('<div class="stCardContainer">', unsafe_allow_html=True)
        st.markdown("<h3>綜合交易建議</h3>", unsafe_allow_html=True)
        
        # 檢查 SMC 和 SNR 建議是否一致
        is_consistent = smc_data["recommendation"] == snr_data["recommendation"]
        confidence = 0.8 if is_consistent else 0.6
        
        # 決定最終建議
        if is_consistent:
            final_rec = smc_data["recommendation"]
        elif smc_data["trend_strength"] > 0.7:
            final_rec = smc_data["recommendation"]
        elif snr_data["rsi"] < 30 or snr_data["rsi"] > 70:
            final_rec = snr_data["recommendation"]
        else:
            final_rec = "neutral"
        
        # 計算風險評分
        risk_score = 5
        if smc_data["market_structure"] == "bullish":
            risk_score -= 1
        else:
            risk_score += 1
            
        if snr_data["overbought"]:
            risk_score += 2
        elif snr_data["oversold"]:
            risk_score -= 2
            
        if final_rec == "buy":
            risk_score += 1
        elif final_rec == "sell":
            risk_score -= 1
            
        risk_score = max(1, min(10, risk_score))
        
        # 顯示綜合建議
        recommendation_color = "#4CAF50" if final_rec == "buy" else "#F44336" if final_rec == "sell" else "#FFC107"
        
        st.markdown(f"""
        <div style="display:flex; align-items:center; margin-bottom:20px;">
            <div style="font-size:28px; font-weight:bold; margin-right:15px; color:{recommendation_color};">
                {"買入" if final_rec == "buy" else "賣出" if final_rec == "sell" else "觀望"}
            </div>
            <div style="flex-grow:1;">
                <div style="height:10px; background-color:rgba(255,255,255,0.1); border-radius:5px;">
                    <div style="height:100%; width:{confidence*100}%; background-color:{recommendation_color}; border-radius:5px;"></div>
                </div>
                <div style="font-size:12px; margin-top:5px;">信心指數: {confidence*100:.1f}%</div>
            </div>
        </div>
        
        <div class="analysis-summary">
            <p><strong>市場結構:</strong> {selected_symbol} 目前處於{"上升" if smc_data["market_structure"] == "bullish" else "下降"}趨勢，趨勢強度為 {smc_data["trend_strength"]:.2f}。</p>
            <p><strong>技術指標:</strong> RSI為 {snr_data["rsi"]:.2f}，{"顯示超買信號" if snr_data["overbought"] else "顯示超賣信號" if snr_data["oversold"] else "處於中性區間"}。</p>
            <p><strong>風險評分:</strong> {risk_score}/10 ({"高風險" if risk_score > 7 else "中等風險" if risk_score > 4 else "低風險"})</p>
        </div>
        """, unsafe_allow_html=True)
        
        # 使用可折疊區域顯示完整的分析報告
        with st.expander("查看完整分析報告"):
            with st.spinner("正在生成完整分析報告..."):
                # 使用真實API進行整合分析
                claude_analysis = get_claude_analysis(selected_symbol, selected_timeframe, smc_data, snr_data)
                st.markdown(claude_analysis)
                
        st.markdown('</div>', unsafe_allow_html=True)

with tabs[1]:
    # AI 分析標籤內容
    st.markdown("<h2>AI 驅動分析</h2>", unsafe_allow_html=True)
    
    if st.session_state.get('analyzed', False):
        # AI 分析分為兩列
        col1, col2 = st.columns(2)
        
        with col1:
            # GPT-4o-mini 市場情緒分析
            st.markdown('<div class="stCardContainer">', unsafe_allow_html=True)
            st.markdown("<h3>市場情緒分析 <span style='font-size:14px; color:#00BCD4;'>(GPT-4o-mini)</span></h3>", unsafe_allow_html=True)
            
            with st.spinner("正在使用 GPT-4o-mini 分析市場情緒..."):
                # 使用真實API進行市場情緒分析
                gpt4o_analysis = get_gpt4o_analysis(selected_symbol, selected_timeframe, smc_data, snr_data)
                st.markdown(gpt4o_analysis)
                
            st.markdown('</div>', unsafe_allow_html=True)
            
        with col2:
            # DeepSeek 策略分析
            st.markdown('<div class="stCardContainer">', unsafe_allow_html=True)
            st.markdown("<h3>策略預測 <span style='font-size:14px; color:#9C27B0;'>(DeepSeek)</span></h3>", unsafe_allow_html=True)
            
            with st.spinner("正在使用 DeepSeek 進行策略預測..."):
                # 使用 DessSeek API 進行策略預測
                # 由於沒有單獨的策略預測函數，我們使用部分 Claude 分析
                strategy_prompt = f"""
                請針對{selected_symbol}在{selected_timeframe}時間框架下，根據以下數據提供簡短的交易策略建議：
                
                價格: ${smc_data['price']:.2f}
                市場結構: {"上升趨勢" if smc_data['market_structure'] == 'bullish' else "下降趨勢"}
                趨勢強度: {smc_data['trend_strength']:.2f}
                RSI: {snr_data['rsi']:.2f}
                支撐位: ${snr_data['near_support']:.2f}
                阻力位: ${snr_data['near_resistance']:.2f}
                
                請僅提供3-4個具體的交易策略建議，包括進場點、目標價和止損位。以Markdown格式回答。
                """
                
                try:
                    # 如果有DeepSeek API密鑰，使用API
                    if DEEPSEEK_API_KEY:
                        headers = {
                            "Content-Type": "application/json",
                            "Authorization": f"Bearer {DEEPSEEK_API_KEY}"
                        }
                        
                        payload = {
                            "model": "deepseek-chat",
                            "messages": [
                                {
                                    "role": "user",
                                    "content": strategy_prompt
                                }
                            ],
                            "temperature": 0.3,
                            "max_tokens": 800
                        }
                        
                        response = requests.post(
                            "https://api.deepseek.com/v1/chat/completions",
                            headers=headers,
                            json=payload
                        )
                        
                        if response.status_code == 200:
                            strategy_analysis = response.json()["choices"][0]["message"]["content"]
                        else:
                            strategy_analysis = f"## {selected_symbol} 短期策略建議\n\n"
                            
                            if final_rec == "buy":
                                strategy_analysis += f"""
                                **突破策略**: 若價格突破${snr_data['near_resistance']:.2f}阻力位，且成交量放大，可考慮追漲進場，目標${smc_data['resistance_level']:.2f}，止損設在${(snr_data['near_resistance']*0.99):.2f}。
                                
                                **支撐回調策略**: 若價格回調至${snr_data['near_support']:.2f}支撐位附近，RSI同時回落至50以下，可考慮逢低買入，目標${snr_data['near_resistance']:.2f}，止損設在${(snr_data['near_support']*0.98):.2f}。
                                """
                            elif final_rec == "sell":
                                strategy_analysis += f"""
                                **做空策略**: 若價格在${snr_data['near_resistance']:.2f}阻力位附近遇阻，RSI高於60，可考慮做空，目標${snr_data['near_support']:.2f}，止損設在${(snr_data['near_resistance']*1.02):.2f}。
                                
                                **高點拋售策略**: 若持倉且價格接近${smc_data['resistance_level']:.2f}，可考慮獲利了結，避免回調風險。
                                """
                            else:
                                strategy_analysis += f"""
                                **區間震盪策略**: 價格可能在${snr_data['near_support']:.2f}-${snr_data['near_resistance']:.2f}之間震盪，可考慮在區間下沿買入，上沿賣出的高頻操作策略。
                                
                                **觀望策略**: 目前市場信號混合，建議觀望至趨勢明確，可關注${snr_data['near_support']:.2f}和${snr_data['near_resistance']:.2f}的突破情況。
                                """
                            
                            strategy_analysis += f"""
                            **風險評估**: 目前市場風險{"偏高" if risk_score > 7 else "偏中性" if risk_score > 4 else "偏低"}，建議使用不超過{30 if risk_score < 5 else 20 if risk_score < 8 else 10}%的資金參與此類交易。
                            """
                    else:
                        # 如果沒有API密鑰，使用預設分析
                        strategy_analysis = f"## {selected_symbol} 短期策略建議\n\n"
                        
                        if final_rec == "buy":
                            strategy_analysis += f"""
                            **突破策略**: 若價格突破${snr_data['near_resistance']:.2f}阻力位，且成交量放大，可考慮追漲進場，目標${smc_data['resistance_level']:.2f}，止損設在${(snr_data['near_resistance']*0.99):.2f}。
                            
                            **支撐回調策略**: 若價格回調至${snr_data['near_support']:.2f}支撐位附近，RSI同時回落至50以下，可考慮逢低買入，目標${snr_data['near_resistance']:.2f}，止損設在${(snr_data['near_support']*0.98):.2f}。
                            """
                        elif final_rec == "sell":
                            strategy_analysis += f"""
                            **做空策略**: 若價格在${snr_data['near_resistance']:.2f}阻力位附近遇阻，RSI高於60，可考慮做空，目標${snr_data['near_support']:.2f}，止損設在${(snr_data['near_resistance']*1.02):.2f}。
                            
                            **高點拋售策略**: 若持倉且價格接近${smc_data['resistance_level']:.2f}，可考慮獲利了結，避免回調風險。
                            """
                        else:
                            strategy_analysis += f"""
                            **區間震盪策略**: 價格可能在${snr_data['near_support']:.2f}-${snr_data['near_resistance']:.2f}之間震盪，可考慮在區間下沿買入，上沿賣出的高頻操作策略。
                            
                            **觀望策略**: 目前市場信號混合，建議觀望至趨勢明確，可關注${snr_data['near_support']:.2f}和${snr_data['near_resistance']:.2f}的突破情況。
                            """
                        
                        strategy_analysis += f"""
                        **風險評估**: 目前市場風險{"偏高" if risk_score > 7 else "偏中性" if risk_score > 4 else "偏低"}，建議使用不超過{30 if risk_score < 5 else 20 if risk_score < 8 else 10}%的資金參與此類交易。
                        """
                        
                except Exception as e:
                    st.error(f"策略分析生成錯誤: {str(e)}")
                    strategy_analysis = "無法生成策略分析，請稍後再試。"
                
                st.markdown(strategy_analysis)
                
            st.markdown('</div>', unsafe_allow_html=True)
        
        # 整合 AI 分析結果 (DeepSeek V3)
        st.markdown('<div class="stCardContainer">', unsafe_allow_html=True)
        st.markdown("<h3>整合 AI 分析 <span style='font-size:14px; color:#3F51B5;'>(DeepSeek V3)</span></h3>", unsafe_allow_html=True)
        
        with st.spinner("正在使用 DeepSeek V3 整合分析結果..."):
            # 這裡已經在上一頁面生成了Claude分析，直接顯示
            st.markdown(claude_analysis)
            
        st.markdown('</div>', unsafe_allow_html=True)
    else:
        # 顯示占位符提示
        st.info("請在「技術分析」頁面選擇加密貨幣並點擊「開始分析」按鈕來產生 AI 分析。")

with tabs[2]:
    # 市場數據標籤內容
    st.markdown("<h2>市場數據</h2>", unsafe_allow_html=True)
    
    # 創建市場概覽卡片
    st.markdown('<div class="stCardContainer">', unsafe_allow_html=True)
    st.markdown("<h3>市場概覽</h3>", unsafe_allow_html=True)
    
    # 嘗試獲取真實市場數據
    try:
        # 使用DexScreener API獲取比特幣數據來估算市場狀況
        btc_data = get_dexscreener_data("BTC/USDT", "1d", limit=2)
        eth_data = get_dexscreener_data("ETH/USDT", "1d", limit=2)
        
        # 計算比特幣24小時變化百分比
        if btc_data is not None and len(btc_data) >= 2:
            btc_change = ((btc_data['close'].iloc[-1] - btc_data['close'].iloc[-2]) / btc_data['close'].iloc[-2]) * 100
        else:
            btc_change = 0
            
        # 計算以太坊24小時變化百分比    
        if eth_data is not None and len(eth_data) >= 2:
            eth_change = ((eth_data['close'].iloc[-1] - eth_data['close'].iloc[-2]) / eth_data['close'].iloc[-2]) * 100
        else:
            eth_change = 0
            
        # 估算恐懼貪婪指數 (簡單模型)
        # 使用比特幣價格變化和交易量來估算
        # 這只是一個簡單的估算，實際的恐懼貪婪指數考慮更多因素
        if btc_data is not None:
            btc_vol_change = 0
            if len(btc_data) >= 2:
                btc_vol_change = ((btc_data['volume'].iloc[-1] - btc_data['volume'].iloc[-2]) / btc_data['volume'].iloc[-2]) * 100
            
            # 估算恐懼貪婪指數：50為中性，根據價格和交易量變化調整
            fear_greed = 50 + (btc_change * 1.5) + (btc_vol_change * 0.5)
            # 限制在0-100範圍內
            fear_greed = max(0, min(100, fear_greed))
            fear_greed = int(fear_greed)
            
            # 判斷變化方向
            fear_greed_change = "+8" if btc_change > 0 else "-8"
        else:
            fear_greed = 50
            fear_greed_change = "0"
            
        # 使用真實數據獲取市值 (使用BTC價格和估算的比例)
        if btc_data is not None:
            btc_price = btc_data['close'].iloc[-1]
            # 估算BTC市值 (已知比特幣流通量約1900萬)
            btc_market_cap = btc_price * 19000000 / 1000000000  # 單位：十億美元
            
            # 假設BTC主導率約為50%來估算總市值
            total_market_cap = btc_market_cap / 0.50  # 假設BTC佔總市值的50%
            
            # 估算24h成交量 (假設是市值的4%)
            total_volume = total_market_cap * 0.04
        else:
            btc_market_cap = 1000
            total_market_cap = 2000
            total_volume = 80
            
    except Exception as e:
        st.error(f"獲取市場數據時出錯: {str(e)}")
        # 使用預設值
        btc_change = 2.4
        eth_change = 1.8
        fear_greed = 65
        fear_greed_change = "+8"
        btc_market_cap = 1000
        total_market_cap = 2000
        total_volume = 80
    
    # 使用列布局顯示市場概覽數據
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("比特幣主導率", f"{50.0:.1f}%", f"{'+' if btc_change > eth_change else '-'}{abs(btc_change - eth_change):.1f}%")
    
    with col2:
        st.metric("市場總市值", f"${total_market_cap:.1f}T", f"{'+' if btc_change > 0 else ''}{btc_change:.1f}%")
    
    with col3:
        st.metric("24h成交量", f"${total_volume:.1f}B", f"{'+' if btc_change > 0 else ''}{btc_change * 1.2:.1f}%")
    
    with col4:
        st.metric("恐懼貪婪指數", f"{fear_greed}", fear_greed_change)
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # 創建熱門加密貨幣數據表格
    st.markdown('<div class="stCardContainer">', unsafe_allow_html=True)
    st.markdown("<h3>熱門加密貨幣</h3>", unsafe_allow_html=True)
    
    # 嘗試獲取真實市場數據
    crypto_list = ['BTC/USDT', 'ETH/USDT', 'SOL/USDT', 'BNB/USDT', 'XRP/USDT', 'ADA/USDT', 'DOGE/USDT', 'SHIB/USDT']
    market_data_list = []
    
    with st.spinner("正在獲取市場數據..."):
        for symbol in crypto_list:
            try:
                # 獲取當日數據
                df = get_dexscreener_data(symbol, "1d", limit=8)
                
                if df is not None and len(df) > 0:
                    # 獲取最新價格
                    current_price = df['close'].iloc[-1]
                    
                    # 計算24小時變化百分比
                    if len(df) >= 2:
                        change_24h = ((df['close'].iloc[-1] - df['close'].iloc[-2]) / df['close'].iloc[-2]) * 100
                    else:
                        change_24h = 0
                        
                    # 計算7天變化百分比
                    if len(df) >= 8:
                        change_7d = ((df['close'].iloc[-1] - df['close'].iloc[-8]) / df['close'].iloc[-8]) * 100
                    else:
                        change_7d = 0
                        
                    # 估算市值 (使用固定的流通量估算)
                    market_cap_map = {
                        'BTC/USDT': 19000000,  # BTC 流通量約1900萬
                        'ETH/USDT': 120000000,  # ETH 流通量約1.2億
                        'SOL/USDT': 440000000,  # SOL 流通量約4.4億
                        'BNB/USDT': 155000000,  # BNB 流通量約1.55億
                        'XRP/USDT': 58000000000,  # XRP 流通量約580億
                        'ADA/USDT': 36000000000,  # ADA 流通量約360億
                        'DOGE/USDT': 145000000000,  # DOGE 流通量約1450億
                        'SHIB/USDT': 589000000000000  # SHIB 流通量約589萬億
                    }
                    
                    circulation = market_cap_map.get(symbol, 1000000)
                    market_cap = current_price * circulation / 1000000000  # 十億美元
                    
                    # 估算24小時成交量 (使用當前價格和成交量估算)
                    volume_24h = df['volume'].iloc[-1] / 1000000000  # 十億美元
                    
                    # 添加到數據列表
                    symbol_name = symbol.split('/')[0]
                    market_data_list.append({
                        '幣種': {
                            'BTC/USDT': '比特幣',
                            'ETH/USDT': '以太坊',
                            'SOL/USDT': '索拉納',
                            'BNB/USDT': '幣安幣',
                            'XRP/USDT': '瑞波幣',
                            'ADA/USDT': '艾達幣',
                            'DOGE/USDT': '狗狗幣',
                            'SHIB/USDT': '柴犬幣'
                        }.get(symbol, symbol),
                        '代碼': symbol_name,
                        '價格(USDT)': current_price,
                        '24h漲跌幅': f"{'+' if change_24h > 0 else ''}{change_24h:.1f}%",
                        '7d漲跌幅': f"{'+' if change_7d > 0 else ''}{change_7d:.1f}%",
                        '市值(十億)': market_cap,
                        '24h成交量(十億)': volume_24h
                    })
                
            except Exception as e:
                st.error(f"獲取 {symbol} 數據時出錯: {str(e)}")
    
    # 如果無法獲取真實數據，使用模擬數據
    if not market_data_list:
        market_data_list = [
            {'幣種': '比特幣', '代碼': 'BTC', '價格(USDT)': 48750.25, '24h漲跌幅': '+2.4%', '7d漲跌幅': '+8.3%', '市值(十億)': 950.2, '24h成交量(十億)': 28.5},
            {'幣種': '以太坊', '代碼': 'ETH', '價格(USDT)': 2820.35, '24h漲跌幅': '+1.8%', '7d漲跌幅': '+12.7%', '市值(十億)': 339.5, '24h成交量(十億)': 12.3},
            {'幣種': '索拉納', '代碼': 'SOL', '價格(USDT)': 142.87, '24h漲跌幅': '+5.7%', '7d漲跌幅': '+22.5%', '市值(十億)': 62.8, '24h成交量(十億)': 4.5},
            {'幣種': '幣安幣', '代碼': 'BNB', '價格(USDT)': 610.23, '24h漲跌幅': '-0.8%', '7d漲跌幅': '+4.8%', '市值(十億)': 94.3, '24h成交量(十億)': 2.1},
            {'幣種': '瑞波幣', '代碼': 'XRP', '價格(USDT)': 0.583, '24h漲跌幅': '+0.5%', '7d漲跌幅': '-2.3%', '市值(十億)': 33.7, '24h成交量(十億)': 1.8},
            {'幣種': '艾達幣', '代碼': 'ADA', '價格(USDT)': 0.452, '24h漲跌幅': '-1.2%', '7d漲跌幅': '+3.8%', '市值(十億)': 16.2, '24h成交量(十億)': 0.7},
            {'幣種': '狗狗幣', '代碼': 'DOGE', '價格(USDT)': 0.128, '24h漲跌幅': '+3.5%', '7d漲跌幅': '+15.2%', '市值(十億)': 18.5, '24h成交量(十億)': 1.2},
            {'幣種': '柴犬幣', '代碼': 'SHIB', '價格(USDT)': 0.00001835, '24h漲跌幅': '+12.4%', '7d漲跌幅': '+28.7%', '市值(十億)': 10.8, '24h成交量(十億)': 2.4}
        ]
    
    # 創建DataFrame
    market_data = pd.DataFrame(market_data_list)
    
    # 為價格上升項目添加綠色，下降項目添加紅色
    def color_change(val):
        if isinstance(val, str) and '+' in val:
            return f'color: #4CAF50; font-weight: bold;'
        elif isinstance(val, str) and '-' in val:
            return f'color: #F44336; font-weight: bold;'
        return ''
    
    # 使用applymap而不是map
    styled_market_data = market_data.style.applymap(color_change, subset=['24h漲跌幅', '7d漲跌幅'])
    
    # 顯示樣式化的表格
    st.dataframe(styled_market_data, use_container_width=True)
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # 創建市場趨勢可視化
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown('<div class="stCardContainer">', unsafe_allow_html=True)
        st.markdown("<h3>主要代幣市值份額</h3>", unsafe_allow_html=True)
        
        # 使用實際市值數據創建餅圖
        if len(market_data_list) > 0:
            labels = [item['代碼'] for item in market_data_list]
            values = [item['市值(十億)'] for item in market_data_list]
            
            # 計算總市值和百分比
            total = sum(values)
            percentages = [value / total * 100 for value in values]
            
            # 使用實際數據創建餅圖
            fig = go.Figure(data=[go.Pie(
                labels=labels,
                values=percentages,
                hole=.4,
                marker_colors=['#F7931A', '#627EEA', '#00FFA3', '#F3BA2F', '#23292F', '#3CC8C8', '#C3A634', '#E0E0E0']
            )])
        else:
            # 使用模擬數據創建餅圖
            labels = ['BTC', 'ETH', 'SOL', 'BNB', 'XRP', 'ADA', 'DOGE', '其他']
            values = [51.2, 18.4, 3.4, 5.1, 1.8, 0.9, 1.0, 18.2]
            
            fig = go.Figure(data=[go.Pie(
                labels=labels,
                values=values,
                hole=.4,
                marker_colors=['#F7931A', '#627EEA', '#00FFA3', '#F3BA2F', '#23292F', '#3CC8C8', '#C3A634', '#E0E0E0']
            )])
        
        fig.update_layout(
            template='plotly_dark',
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            margin=dict(l=20, r=20, t=30, b=20),
            height=300
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="stCardContainer">', unsafe_allow_html=True)
        st.markdown("<h3>7日漲跌幅比較</h3>", unsafe_allow_html=True)
        
        # 使用實際市值數據創建條形圖
        if len(market_data_list) > 0:
            coins = [item['代碼'] for item in market_data_list]
            changes = [float(item['7d漲跌幅'].replace('%', '').replace('+', '')) for item in market_data_list]
            
            # 為正負值設定不同顏色
            colors = ['#4CAF50' if c > 0 else '#F44336' for c in changes]
            
            fig = go.Figure(data=[go.Bar(
                x=coins,
                y=changes,
                marker_color=colors
            )])
        else:
            # 使用模擬數據創建條形圖
            coins = ['BTC', 'ETH', 'SOL', 'BNB', 'XRP', 'ADA', 'DOGE', 'SHIB']
            changes = [8.3, 12.7, 22.5, 4.8, -2.3, 3.8, 15.2, 28.7]
            
            # 為正負值設定不同顏色
            colors = ['#4CAF50' if c > 0 else '#F44336' for c in changes]
            
            fig = go.Figure(data=[go.Bar(
                x=coins,
                y=changes,
                marker_color=colors
            )])
        
        fig.update_layout(
            title='7日漲跌幅 (%)',
            template='plotly_dark',
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            margin=dict(l=20, r=20, t=60, b=20),
            height=300
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        st.markdown('</div>', unsafe_allow_html=True)

with tabs[3]:
    # 設置標籤內容
    st.markdown("<h2>設置</h2>", unsafe_allow_html=True)
    
    # 創建設置卡片
    st.markdown('<div class="stCardContainer">', unsafe_allow_html=True)
    st.markdown("<h3>應用設置</h3>", unsafe_allow_html=True)
    
    # 主題設置
    st.radio("主題", ["深色模式", "淺色模式"], index=0)
    
    # 默認圖表時間範圍
    st.select_slider("默認圖表時間範圍", options=["50", "100", "200", "500", "全部"], value="100")
    
    # 顯示設置
    st.checkbox("顯示交易量圖表", value=True)
    st.checkbox("顯示移動平均線", value=True)
    st.checkbox("顯示支撐/阻力位", value=True)
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # API 設置卡片
    st.markdown('<div class="stCardContainer">', unsafe_allow_html=True)
    st.markdown("<h3>API 設置</h3>", unsafe_allow_html=True)
    
    # OpenAI API 設置
    openai_key = st.text_input("OpenAI API 密鑰", type="password", value="*" * 10 if OPENAI_API_KEY else "")
    
    # DeepSeek API 設置
    deepseek_key = st.text_input("DeepSeek API 密鑰", type="password", value="*" * 10 if DEEPSEEK_API_KEY else "")
    
    # CoinMarketCap API 設置
    cmc_key = st.text_input("CoinMarketCap API 密鑰", type="password", value="*" * 10 if COINMARKETCAP_API_KEY else "")
    
    # 保存按鈕
    st.button("保存設置")
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # 關於應用卡片
    st.markdown('<div class="stCardContainer">', unsafe_allow_html=True)
    st.markdown("<h3>關於</h3>", unsafe_allow_html=True)
    
    st.markdown("""
    **0xAI CryptoCat** 是一個使用多模型 AI 技術的加密貨幣分析工具，結合了技術分析和 AI 驅動的市場分析。
    
    **版本**: v1.0.0
    
    **開發者**: Terry Lee
    
    **使用的 AI 模型**:
    - DeepSeek V3 (技術分析和整合分析)
    - GPT-4o-mini (市場情緒分析)
    
    **數據來源**:
    - DexScreener API
    - Coincap API
    - CoinMarketCap API
    """)
    
    st.markdown('</div>', unsafe_allow_html=True)

# 移除底部 Streamlit 水印
st.markdown("""
<style>
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)
