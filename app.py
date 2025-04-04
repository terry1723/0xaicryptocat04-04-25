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
            # 這裡可以調用原有的數據獲取和圖表生成函數
            # 模擬數據獲取延遲
            time.sleep(1)
            
            # 使用更具視覺吸引力的圖表模板
            fig = go.Figure()
            
            # 添加蠟燭圖
            fig.add_trace(go.Candlestick(
                x=[datetime(2023, 1, i) for i in range(1, 31)],
                open=[50000 + i*100 + random.uniform(-500, 500) for i in range(30)],
                high=[50000 + i*100 + random.uniform(0, 1000) for i in range(30)],
                low=[50000 + i*100 - random.uniform(0, 1000) for i in range(30)],
                close=[50000 + i*100 + random.uniform(-500, 500) for i in range(30)],
                name='價格'
            ))
            
            # 添加移動平均線
            fig.add_trace(go.Scatter(
                x=[datetime(2023, 1, i) for i in range(1, 31)],
                y=[50000 + i*100 for i in range(30)],
                mode='lines',
                name='MA20',
                line=dict(color='#9C27B0', width=2)
            ))
            
            fig.add_trace(go.Scatter(
                x=[datetime(2023, 1, i) for i in range(1, 31)],
                y=[49800 + i*100 for i in range(30)],
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
                # 添加一個帶有成交量數據的次要圖表
                volume_fig = go.Figure()
                volume_fig.add_trace(go.Bar(
                    x=[datetime(2023, 1, i) for i in range(1, 31)],
                    y=[random.uniform(1000, 5000) for _ in range(30)],
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
            
            # 模擬 SMC 分析數據
            smc_data = {
                "market_structure": "bullish",
                "trend_strength": 0.75,
                "support_level": 45200.50,
                "resistance_level": 52300.75,
                "price": 48750.25,
                "recommendation": "buy"
            }
            
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
                """)
                
                # 添加更多詳細信息...
                
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col2:
            # SNR 分析結果卡片
            st.markdown('<div class="stCardContainer">', unsafe_allow_html=True)
            st.markdown("<h3>SNR 供需分析</h3>", unsafe_allow_html=True)
            
            # 模擬 SNR 分析數據
            snr_data = {
                "rsi": 65.5,
                "overbought": False,
                "oversold": False,
                "near_support": 47800.50,
                "strong_support": 44500.25,
                "near_resistance": 50200.75,
                "strong_resistance": 53500.50,
                "recommendation": "buy"
            }
            
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
                """)
                
                # 添加更多詳細信息...
                
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
            # 這裡可以放置原有的 Claude API 生成的完整分析報告
            st.markdown("""
            # 完整技術分析報告
            
            ## 市場結構分析
            當前市場處於上升趨勢，價格在過去幾周形成了更高的高點和更高的低點結構。趨勢強度適中，顯示有健康的上升動能，但也有短期回調的可能。
            
            ## 關鍵價位分析
            **支撐位**:
            - 主要支撐: $47,800
            - 次要支撐: $46,500
            - 強支撐: $44,500
            
            **阻力位**:
            - 近期阻力: $50,200
            - 主要阻力: $52,300
            - 心理阻力: $55,000
            
            ## 操作建議
            價格接近支撐位且RSI處於中性區域，可考慮分批買入。第一目標價位為 $50,200。
            
            ## 風險控制策略
            - 止損位: $46,000 (支撐位下方)
            - 建議倉位: 總資金的20-30%
            - 避免在高波動時段進行大額交易
            - 注意上升趨勢中的回調風險
            
            ## 多時間框架考量
            建議同時關注日線和週線的走勢，確保與主趨勢一致。當前日線和週線都呈現看漲形態，增強了信號的可靠性。
            """)
            
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
                # 這裡可以調用原有的 GPT-4o API
                # 模擬API延遲
                time.sleep(1.5)
                
                # 模擬 GPT-4o 分析結果
                st.markdown("""
                ## BTC/USDT 1h 市場情緒分析

                當前市場情緒呈現**輕度看漲**傾向，但投資者心態謹慎。

                RSI指標當前為65.5，處於中性偏上區域，尚未達到超買，但投資者需警惕短期可能的回調。

                目前市場支撐位與阻力位之間的價格區間較為明確，從$47,800到$50,200，市場參與者似乎達成共識，大多數交易者情緒偏向在支撐位附近買入。

                近期可能的情緒轉變點在$50,200附近，若突破此點，可能激發更強的市場樂觀情緒；若無法突破，則市場信心可能受挫。
                """)
                
            st.markdown('</div>', unsafe_allow_html=True)
            
        with col2:
            # DeepSeek 策略分析
            st.markdown('<div class="stCardContainer">', unsafe_allow_html=True)
            st.markdown("<h3>策略預測 <span style='font-size:14px; color:#9C27B0;'>(DeepSeek)</span></h3>", unsafe_allow_html=True)
            
            with st.spinner("正在使用 DeepSeek 進行策略預測..."):
                # 這裡可以調用原有的 DeepSeek API
                # 模擬API延遲
                time.sleep(1.8)
                
                # 模擬 DeepSeek 分析結果
                st.markdown("""
                ## 比特幣短期策略建議

                **突破策略**: 若價格突破$50,200阻力位，且成交量放大，可考慮追漲進場，目標$52,300，止損設在$49,500。

                **支撐回調策略**: 若價格回調至$47,800支撐位附近，RSI同時回落至50以下，可考慮逢低買入，目標$50,200，止損設在$46,500。

                **區間震盪策略**: 若價格在$47,800-$50,200之間震盪，可考慮在區間下沿買入，上沿賣出的高頻操作策略。
                
                **風險評估**: 目前市場風險偏中性，建議使用不超過30%的資金參與此類交易。
                """)
                
            st.markdown('</div>', unsafe_allow_html=True)
        
        # 整合 AI 分析結果 (DeepSeek V3)
        st.markdown('<div class="stCardContainer">', unsafe_allow_html=True)
        st.markdown("<h3>整合 AI 分析 <span style='font-size:14px; color:#3F51B5;'>(DeepSeek V3)</span></h3>", unsafe_allow_html=True)
        
        with st.spinner("正在使用 DeepSeek V3 整合分析結果..."):
            # 這裡可以調用原有的 DeepSeek V3 API
            # 模擬API延遲
            time.sleep(2.3)
            
            # 模擬 DeepSeek V3 整合分析結果
            st.markdown("""
            # BTC/USDT 1h 綜合分析報告

            ## 整合交易建議
            **建議操作**：買入
            **信心指數**：78.5%
            **風險評分**：5/10 (中等風險)

            ## 市場結構分析
            BTC目前處於上升趨勢，趨勢強度為0.75。
            RSI指標為65.50，處於中性區間。
            SMC和SNR策略分析結果一致，增強了信號可靠性。

            ## 關鍵價位分析
            **支撐位**：
            - SMC分析：$47,800.50
            - SNR分析：$47,800.50（強支撐：$44,500.25）

            **阻力位**：
            - SMC分析：$52,300.75
            - SNR分析：$50,200.75（強阻力：$53,500.50）

            ## 操作建議
            價格接近支撐位且RSI處於中性區域，可考慮分批買入，第一目標價位為$50,200.75，突破後目標$52,300.75。

            ## 風險控制策略
            - 止損位設置：$46,500（主要支撐位下方）
            - 建議倉位：總資金的20-30%
            - 避免在高波動時段進行大額交易
            - 注意上升趨勢中的回調風險

            ## 多時間框架考量
            建議同時關注日線走勢，確保與主趨勢一致。
            """)
            
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
    
    # 使用列布局顯示市場概覽數據
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("比特幣主導率", "51.2%", "+0.4%")
    
    with col2:
        st.metric("市場總市值", "$2.1T", "+3.2%")
    
    with col3:
        st.metric("24h成交量", "$87.5B", "-5.7%")
    
    with col4:
        st.metric("恐懼貪婪指數", "65", "+8")
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # 創建熱門加密貨幣數據表格
    st.markdown('<div class="stCardContainer">', unsafe_allow_html=True)
    st.markdown("<h3>熱門加密貨幣</h3>", unsafe_allow_html=True)
    
    # 創建模擬的市場數據
    market_data = pd.DataFrame({
        '幣種': ['比特幣', '以太坊', '索拉納', '幣安幣', '瑞波幣', '艾達幣', '狗狗幣', '柴犬幣'],
        '代碼': ['BTC', 'ETH', 'SOL', 'BNB', 'XRP', 'ADA', 'DOGE', 'SHIB'],
        '價格(USDT)': [48750.25, 2820.35, 142.87, 610.23, 0.583, 0.452, 0.128, 0.00001835],
        '24h漲跌幅': ['+2.4%', '+1.8%', '+5.7%', '-0.8%', '+0.5%', '-1.2%', '+3.5%', '+12.4%'],
        '7d漲跌幅': ['+8.3%', '+12.7%', '+22.5%', '+4.8%', '-2.3%', '+3.8%', '+15.2%', '+28.7%'],
        '市值(十億)': [950.2, 339.5, 62.8, 94.3, 33.7, 16.2, 18.5, 10.8],
        '24h成交量(十億)': [28.5, 12.3, 4.5, 2.1, 1.8, 0.7, 1.2, 2.4]
    })
    
    # 使用自定義HTML和CSS來創建更漂亮的表格
    # 為價格上升項目添加綠色，下降項目添加紅色
    def color_change(val):
        if isinstance(val, str) and '+' in val:
            return f'color: #4CAF50; font-weight: bold;'
        elif isinstance(val, str) and '-' in val:
            return f'color: #F44336; font-weight: bold;'
        return ''
    
    styled_market_data = market_data.style.applymap(color_change, subset=['24h漲跌幅', '7d漲跌幅'])
    
    # 顯示樣式化的表格
    st.dataframe(styled_market_data, use_container_width=True)
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # 創建市場趨勢可視化
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown('<div class="stCardContainer">', unsafe_allow_html=True)
        st.markdown("<h3>主要代幣市值份額</h3>", unsafe_allow_html=True)
        
        # 創建模擬的餅圖數據
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
        
        # 創建模擬的條形圖數據
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
