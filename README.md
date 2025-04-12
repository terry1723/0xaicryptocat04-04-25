# 0xAI Crypto Cat 分析應用

基於 Streamlit 構建的加密貨幣分析工具，集成了多種數據源和 AI 分析功能。

## 功能特點

- 從多個數據源獲取加密貨幣價格數據（DexScreener、Coincap、CoinMarketCap）
- 技術分析工具（SMC、SNR 分析）
- 多時間框架分析支持
- AI 驅動的市場分析和預測
- 交互式圖表和數據可視化

## 最新更新

- 添加 Zeabur 自動部署支持
- 添加 DexScreener API 整合，提高數據可靠性
- 優化錯誤處理和備用數據獲取策略
- 改進 API 密鑰管理機制
- 優化環境變數處理，支援多種部署環境

## 部署說明

### 本地運行

1. 克隆存儲庫：
   ```
   git clone https://github.com/terry1723/0xaicryoptocat12-4-25.git
   cd 0xaicryoptocat12-4-25
   ```

2. 安裝依賴：
   ```
   pip install -r requirements.txt
   ```

3. **設置 API 密鑰（兩種方法）**：

   **方法 1：使用環境變數（推薦）**
   ```
   # Linux/Mac
   export DEEPSEEK_API_KEY="your_deepseek_api_key"
   export COINMARKETCAP_API_KEY="your_coinmarketcap_api_key"
   
   # Windows
   set DEEPSEEK_API_KEY=your_deepseek_api_key
   set COINMARKETCAP_API_KEY=your_coinmarketcap_api_key
   ```

   **方法 2：使用 secrets.toml**
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

部署到雲平台（如 Streamlit Cloud、Zeabur、Heroku 等）時，請確保：

1. **在平台上設置環境變量**（強烈推薦）：
   - `DEEPSEEK_API_KEY`
   - `COINMARKETCAP_API_KEY`

2. 對於 Streamlit Cloud：
   - 在 Streamlit Cloud 的設置頁面添加這些密鑰
   - 或使用 GitHub repository secrets

3. 對於 Zeabur：
   - 在 Zeabur 控制台中找到應用設置
   - 添加環境變數部分，輸入 API 密鑰

4. 對於 Heroku：
   ```
   heroku config:set DEEPSEEK_API_KEY=your_deepseek_api_key
   heroku config:set COINMARKETCAP_API_KEY=your_coinmarketcap_api_key
   ```

## 技術架構

- 前端：Streamlit
- 數據源：DexScreener API、Coincap API、CoinMarketCap API
- 數據處理：Pandas、NumPy
- 可視化：Plotly

## 故障排除

### 解決 "No secrets files found" 錯誤
如果遇到 `StreamlitSecretNotFoundError` 或 "No secrets files found" 錯誤：

1. **優先使用環境變數**：本應用已優化為首先讀取環境變數，這是雲部署的推薦方式

2. 如果使用 secrets.toml：
   - 確保文件位於正確路徑（`.streamlit/secrets.toml`）
   - 檢查文件格式是否正確
   - 確認密鑰名稱與代碼中一致

3. 確認部署平台上已正確配置相應的環境變數或密鑰 