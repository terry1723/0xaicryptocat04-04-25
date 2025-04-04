# 0xAI Crypto Cat 分析應用

基於 Streamlit 構建的加密貨幣分析工具，集成了多種數據源和 AI 分析功能。

## 功能特點

- 從多個數據源獲取加密貨幣價格數據（DexScreener、Coincap、CoinMarketCap）
- 技術分析工具（SMC、SNR 分析）
- 多時間框架分析支持
- AI 驅動的市場分析和預測
- 交互式圖表和數據可視化

## 最新更新

- 添加 DexScreener API 整合，提高數據可靠性
- 優化錯誤處理和備用數據獲取策略
- 改進 API 密鑰管理機制

## 部署說明

### 本地運行

1. 克隆存儲庫：
   ```
   git clone https://github.com/terry1723/0xaicryptocat04-04-25.git
   cd 0xaicryptocat04-04-25
   ```

2. 安裝依賴：
   ```
   pip install -r requirements.txt
   ```

3. 創建 `.streamlit/secrets.toml` 文件（如果尚未存在）：
   ```
   mkdir -p .streamlit
   ```
   
   並在 `.streamlit/secrets.toml` 中添加您的 API 密鑰：
   ```
   DEEPSEEK_API_KEY = "your_deepseek_api_key"
   COINMARKETCAP_API_KEY = "your_coinmarketcap_api_key"
   ```

4. 運行應用：
   ```
   streamlit run app.py
   ```

### 部署到雲服務

部署到雲平台（如 Streamlit Cloud、Heroku 等）時，請確保：

1. 在平台上設置環境變量或密鑰：
   - `DEEPSEEK_API_KEY`
   - `COINMARKETCAP_API_KEY`

2. 對於 Streamlit Cloud，可在設置中添加這些密鑰

## 技術架構

- 前端：Streamlit
- 數據源：DexScreener API、Coincap API、CoinMarketCap API
- 數據處理：Pandas、NumPy
- 可視化：Plotly

## 故障排除

如果遇到 `StreamlitSecretNotFoundError` 錯誤：
1. 確保已創建 `.streamlit/secrets.toml` 文件
2. 檢查是否正確設置了環境變量
3. 確認部署平台上已配置相應的密鑰 