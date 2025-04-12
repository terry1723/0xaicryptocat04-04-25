#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
加密貨幣分析工具 v3.3.0
更新內容: 將Crypto APIs提升為主要數據源，優化數據獲取順序
數據獲取優先順序:
1. Crypto APIs (主要數據源)
2. Smithery MCP API
3. CoinCap API 
4. CoinGecko API
"""

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
from dotenv import load_dotenv
import subprocess
import sys

# 加載環境變數
load_dotenv()

# 從環境變數獲取API密鑰
CRYPTOAPIS_KEY = os.getenv('CRYPTOAPIS_KEY', '56af1c06ebd5a7602a660516e0d044489c307860')
BINANCE_API_KEY = os.getenv('BINANCE_API_KEY', '')  # 默認為空字符串，避免硬編碼密鑰
BINANCE_API_SECRET = os.getenv('BINANCE_API_SECRET', '')  # 默認為空字符串，避免硬編碼密鑰

# 設置頁面配置
st.set_page_config(
    page_title="加密貨幣分析工具",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed"
)

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

    /* 登錄表單樣式 */
    .login-container {
        max-width: 450px;
        margin: 0 auto;
        padding: 30px;
        background-color: var(--card-background);
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
    }

    .login-title {
        font-size: 24px;
        font-weight: bold;
        margin-bottom: 20px;
        color: var(--primary-color);
        text-align: center;
    }

    /* 輸入框樣式 */
    .stTextInput > div > div > input {
        background-color: #2a2a2a;
        color: var(--text-color);
        border: 1px solid var(--border-color);
        border-radius: 5px;
        padding: 10px;
    }

    /* 按鈕樣式 */
    .stButton button {
        background-color: var(--primary-color);
        color: white;
        border-radius: 5px;
        border: none;
        padding: 10px 20px;
        font-weight: bold;
        width: 100%;
    }

    .stButton button:hover {
        background-color: #7d32a8;
    }

    /* 標題漸變色彩 */
    .gradient-text {
        background: linear-gradient(90deg, var(--primary-color), var(--secondary-color));
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

# 初始化會話狀態
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

if 'view_mode' not in st.session_state:
    st.session_state.view_mode = 'nymph_strategy'  # 預設顯示女妖策略

# 檢查用戶是否已登錄
if st.session_state.logged_in:
    # 已登錄，執行策略頁面
    try:
        # 根據視圖模式選擇顯示內容
        if st.session_state.view_mode == 'nymph_strategy':
            # 女妖輔助建議策略
            from strategy_tower import *
        else:
            # 其他策略頁面或功能
            st.error("該功能尚未實現")
    except Exception as e:
        st.error(f"無法載入策略頁面: {e}")
        if st.button("登出"):
            st.session_state.logged_in = False
            st.experimental_rerun()
else:
    # 顯示登錄頁面
    st.markdown("<h1 class='gradient-text' style='text-align: center;'>加密貨幣分析與策略工具</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; margin-bottom: 30px;'>登錄以訪問專業交易信號和市場分析工具</p>", unsafe_allow_html=True)
    
    # 創建居中的登錄表單
    st.markdown("<div class='login-container'>", unsafe_allow_html=True)
    st.markdown("<div class='login-title'>用戶登錄</div>", unsafe_allow_html=True)
    
    # 登錄表單
    username = st.text_input("用戶名", placeholder="請輸入用戶名")
    password = st.text_input("密碼", type="password", placeholder="請輸入密碼")
    
    login_button = st.button("登錄")
    
    if login_button:
        # 增加 Terry1723/26436863 作為有效的登錄憑證
        if (username == "Terry1723" and password == "26436863") or (username == "Terry1723" and password == "admin") or (username == "admin" and password == "admin"):
            # 顯示成功消息
            st.success("登錄成功！正在重定向到策略頁面...")
            
            # 更新會話狀態
            st.session_state.logged_in = True
            st.session_state.username = username
            
            # 添加延遲效果，然後重新運行應用程序
            time.sleep(1)
            st.experimental_rerun()
        else:
            st.error("用戶名或密碼錯誤，請重試")
    
    st.markdown("</div>", unsafe_allow_html=True)
    
    # 測試帳號信息
    st.markdown("<div style='text-align: center; margin-top: 20px; font-size: 0.8em;'>測試帳號: Terry1723 | 密碼: 26436863</div>", unsafe_allow_html=True)

# 頁腳
st.markdown("""
<div style="margin-top:50px; padding:20px 0; border-top:1px solid #333; text-align:center; font-size:0.8em; color:#888;">
    © 2025 加密貨幣分析與策略工具 | 本網站提供的加密貨幣分析僅供參考，不構成投資建議
</div>
""", unsafe_allow_html=True)
